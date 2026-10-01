from django.contrib import admin
from .models import ProductionBatch


@admin.register(ProductionBatch)
class ProductionBatchAdmin(admin.ModelAdmin):
	list_display = ('batch_number', 'product', 'production_date', 'quantity_produced', 'recorded_by')
	list_filter = ('production_date', 'product')
	search_fields = ('batch_number', 'product__name')
