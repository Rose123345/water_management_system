from django.contrib import admin
from django.db import transaction

from accounts.admin_mixins import RecordedByAdminMixin
from Inventory.models import StockMovement
from Inventory.services import record_stock_movement

from .models import ProductionBatch


@admin.register(ProductionBatch)
class ProductionBatchAdmin(RecordedByAdminMixin, admin.ModelAdmin):
	recorded_by_field = 'recorded_by'
	list_display = ('batch_number', 'product', 'production_date', 'quantity_produced', 'recorded_by')
	list_filter = ('production_date', 'product')
	search_fields = ('batch_number', 'product__name')

	def get_readonly_fields(self, request, obj=None):
		readonly = super().get_readonly_fields(request, obj)
		if obj:
			# Stock was already added for this batch; changing these would desync inventory.
			readonly += ('product', 'quantity_produced')
		return readonly

	@transaction.atomic
	def save_model(self, request, obj, form, change):
		super().save_model(request, obj, form, change)
		if not change:
			record_stock_movement(
				product=obj.product,
				movement_type=StockMovement.MovementType.PRODUCTION,
				quantity=obj.quantity_produced,
				recorded_by=request.user,
				note=f'Produced from batch {obj.batch_number}',
				production_batch=obj,
			)
