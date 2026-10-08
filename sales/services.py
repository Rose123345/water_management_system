from django.db import transaction

from Inventory.models import StockMovement
from Inventory.services import record_stock_movement

from .models import Order


class OrderStatusError(Exception):
    pass


def _lock(order):
    return Order.objects.select_for_update().get(pk=order.pk)


@transaction.atomic
def advance_order_status(order, user):
    """Move an order one step forward: draft -> confirmed -> completed."""
    order = _lock(order)
    if order.status == Order.Status.DRAFT:
        return _confirm_order(order, user)
    if order.status == Order.Status.CONFIRMED:
        return _complete_order(order)
    raise OrderStatusError(f'{order.get_status_display()} orders cannot be advanced.')


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


def _complete_order(order):
    if order.balance > 0:
        raise OrderStatusError('An order can only be completed once it is fully paid.')
    order.status = Order.Status.COMPLETED
    order.save(update_fields=['status', 'updated_at'])
    return order


@transaction.atomic
def cancel_order(order, user):
    order = _lock(order)
    if order.status == Order.Status.DRAFT:
        pass
    elif order.status == Order.Status.CONFIRMED:
        if order.payments.filter(status='completed').exists():
            raise OrderStatusError('This order has recorded payments and cannot be cancelled.')
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
