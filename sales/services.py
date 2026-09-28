from django.core.exceptions import ValidationError
from django.db import transaction

from Inventory.models import StockMovement
from Inventory.services import record_stock_movement

from .models import Order


class OrderStatusError(Exception):
    pass


@transaction.atomic
def advance_order_status(order, user):
    if order.status != Order.Status.DRAFT:
        raise OrderStatusError('Only draft orders can be confirmed.')
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


@transaction.atomic
def cancel_order(order, user):
    if order.status != Order.Status.DRAFT:
        raise OrderStatusError('Only draft orders can be cancelled.')
    order.status = Order.Status.CANCELLED
    order.save(update_fields=['status', 'updated_at'])
    return order