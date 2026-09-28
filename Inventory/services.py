from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Stock, StockMovement


@transaction.atomic
def record_stock_movement(product, movement_type, quantity, recorded_by=None, note='', production_batch=None):
    if quantity <= 0:
        raise ValidationError('Movement quantity must be greater than zero.')

    stock, _ = Stock.objects.get_or_create(product=product)
    stock = Stock.objects.select_for_update().get(pk=stock.pk)

    if movement_type == StockMovement.MovementType.ISSUE:
        if stock.quantity_on_hand < quantity:
            raise ValidationError('Cannot issue more stock than is currently available.')
        stock.quantity_on_hand -= quantity
    elif movement_type in (StockMovement.MovementType.RECEIPT, StockMovement.MovementType.PRODUCTION):
        stock.quantity_on_hand += quantity
    else:
        raise ValidationError('Unsupported stock movement type.')

    stock.save(update_fields=['quantity_on_hand', 'updated_at'])
    return StockMovement.objects.create(
        product=product,
        movement_type=movement_type,
        quantity=quantity,
        note=note,
        production_batch=production_batch,
        recorded_by=recorded_by,
    )