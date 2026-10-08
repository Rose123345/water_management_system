from django.db import transaction
from django.utils import timezone

from distribution.models import Delivery
from Inventory.models import StockMovement
from Inventory.services import record_stock_movement

from .models import Order


class OrderStatusError(Exception):
    pass


# The delivery status that matches each order status once an order has left the depot.
DELIVERY_STATUS_FOR_ORDER = {
    Order.Status.ON_THE_WAY: Delivery.Status.OUT_FOR_DELIVERY,
    Order.Status.DELIVERED: Delivery.Status.DELIVERED,
}

# Order statuses that follow the delivery record once one exists.
ORDER_STATUS_FOR_DELIVERY = {
    Delivery.Status.OUT_FOR_DELIVERY: Order.Status.ON_THE_WAY,
    Delivery.Status.DELIVERED: Order.Status.DELIVERED,
}


def _lock(order):
    return Order.objects.select_for_update().get(pk=order.pk)


@transaction.atomic
def advance_order_status(order, user):
    """Move an order one step forward: pending -> confirmed -> on the way -> delivered."""
    order = _lock(order)
    if order.status == Order.Status.PENDING:
        return _confirm_order(order, user)
    if order.status == Order.Status.CONFIRMED:
        return _set_status(order, Order.Status.ON_THE_WAY)
    if order.status == Order.Status.ON_THE_WAY:
        return _set_status(order, Order.Status.DELIVERED)
    raise OrderStatusError(f'{order.get_status_display()} orders cannot be moved forward.')


def _confirm_order(order, user):
    if not order.items.exists():
        raise OrderStatusError('An order must contain at least one item.')

    for item in order.items.select_related('product'):
        record_stock_movement(
            item.product,
            StockMovement.MovementType.ISSUE,
            item.quantity,
            recorded_by=user,
            note=f'Order {order.order_number}',
        )

    order.status = Order.Status.CONFIRMED
    order.save(update_fields=['status', 'updated_at'])
    return order


def _set_status(order, status):
    order.status = status
    order.save(update_fields=['status', 'updated_at'])

    delivery = Delivery.objects.filter(order=order).first()
    if delivery:
        delivery.status = DELIVERY_STATUS_FOR_ORDER[status]
        if status == Order.Status.DELIVERED and not delivery.delivered_at:
            delivery.delivered_at = timezone.now()
        delivery.save(update_fields=['status', 'delivered_at'])
    return order


@transaction.atomic
def sync_order_with_delivery(delivery):
    """Keep a confirmed order's status in step with its delivery record."""
    order = _lock(delivery.order)
    if order.status not in (Order.Status.CONFIRMED, Order.Status.ON_THE_WAY, Order.Status.DELIVERED):
        return order
    # A failed or not-yet-dispatched delivery puts the order back to confirmed.
    status = ORDER_STATUS_FOR_DELIVERY.get(delivery.status, Order.Status.CONFIRMED)
    if order.status != status:
        order.status = status
        order.save(update_fields=['status', 'updated_at'])
    return order


@transaction.atomic
def cancel_order(order, user):
    order = _lock(order)
    if order.status in (Order.Status.PENDING, Order.Status.CONFIRMED) and order.payments.filter(
        status='completed'
    ).exists():
        raise OrderStatusError('This order has recorded payments and cannot be cancelled. Please contact us.')

    if order.status == Order.Status.PENDING:
        pass
    elif order.status == Order.Status.CONFIRMED:
        delivery = getattr(order, 'delivery', None)
        if delivery and delivery.status != delivery.Status.FAILED:
            raise OrderStatusError(
                'This order has an active delivery. Mark the delivery as failed before cancelling.'
            )
        for item in order.items.select_related('product'):
            record_stock_movement(
                item.product,
                StockMovement.MovementType.RECEIPT,
                item.quantity,
                recorded_by=user,
                note=f'Returned from cancelled order {order.order_number}',
            )
    else:
        raise OrderStatusError(f'{order.get_status_display()} orders cannot be cancelled.')

    order.status = Order.Status.CANCELLED
    order.save(update_fields=['status', 'updated_at'])
    return order
