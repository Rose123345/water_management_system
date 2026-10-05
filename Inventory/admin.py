from django.contrib import admin

from .forms import StockMovementForm
from .models import Stock, StockMovement
from .services import record_stock_movement


class StockMovementAdminForm(StockMovementForm):
	def clean(self):
		cleaned_data = super().clean()
		if cleaned_data.get('movement_type') == StockMovement.MovementType.ISSUE:
			product = cleaned_data.get('product')
			quantity = cleaned_data.get('quantity')
			stock = Stock.objects.filter(product=product).first() if product else None
			available = stock.quantity_on_hand if stock else 0
			if quantity and quantity > available:
				self.add_error('quantity', 'Cannot issue more stock than is currently available.')
		return cleaned_data


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
	list_display = ('product', 'quantity_on_hand', 'updated_at')
	search_fields = ('product__name',)
	readonly_fields = ('product', 'quantity_on_hand', 'updated_at')

	def get_readonly_fields(self, request, obj=None):
		if obj is None:
			return ('updated_at',)
		return self.readonly_fields

	def save_model(self, request, obj, form, change):
		if not change:
			opening_quantity = obj.quantity_on_hand
			obj.quantity_on_hand = 0
			super().save_model(request, obj, form, change)
			if opening_quantity:
				record_stock_movement(
					product=obj.product,
					movement_type=StockMovement.MovementType.RECEIPT,
					quantity=opening_quantity,
					recorded_by=request.user,
					note='Opening stock entered in Django admin',
				)
			obj.refresh_from_db()
			return
		super().save_model(request, obj, form, change)

	def has_delete_permission(self, request, obj=None):
		return False


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
	form = StockMovementAdminForm
	list_display = ('product', 'movement_type', 'quantity', 'production_batch', 'recorded_by', 'created_at')
	list_filter = ('movement_type', 'created_at')
	search_fields = ('product__name', 'production_batch__batch_number', 'note')
	readonly_fields = (
		'product', 'movement_type', 'quantity', 'note', 'production_batch',
		'recorded_by', 'created_at',
	)

	def get_readonly_fields(self, request, obj=None):
		return self.readonly_fields if obj else ('production_batch', 'recorded_by', 'created_at')

	def get_fields(self, request, obj=None):
		if obj:
			return self.readonly_fields
		return ('product', 'movement_type', 'quantity', 'note')

	def has_change_permission(self, request, obj=None):
		if obj is not None:
			return False
		return super().has_change_permission(request, obj)

	def save_model(self, request, obj, form, change):
		if change:
			raise ValidationError('Stock movement records cannot be edited.')
		movement = record_stock_movement(
			product=obj.product,
			movement_type=obj.movement_type,
			quantity=obj.quantity,
			recorded_by=request.user,
			note=obj.note,
		)
		obj.pk = movement.pk
		obj.created_at = movement.created_at
		obj._state.adding = False
		obj._state.db = movement._state.db

	def has_delete_permission(self, request, obj=None):
		return False
