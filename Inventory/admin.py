from django.contrib import admin
from .models import Stock, StockMovement


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
	list_display = ('product', 'quantity_on_hand', 'updated_at')
	search_fields = ('product__name',)
	readonly_fields = ('product', 'quantity_on_hand', 'updated_at')

	def has_add_permission(self, request):
		return False

	def has_delete_permission(self, request, obj=None):
		return False


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
	list_display = ('product', 'movement_type', 'quantity', 'production_batch', 'recorded_by', 'created_at')
	list_filter = ('movement_type', 'created_at')
	search_fields = ('product__name', 'production_batch__batch_number', 'note')
	readonly_fields = (
		'product', 'movement_type', 'quantity', 'note', 'production_batch',
		'recorded_by', 'created_at',
	)

	def has_add_permission(self, request):
		return False

	def has_delete_permission(self, request, obj=None):
		return False
