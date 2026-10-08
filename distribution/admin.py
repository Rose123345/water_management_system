from django.contrib import admin

from sales.services import sync_order_with_delivery

from .models import Delivery


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
	list_display = ('order', 'status', 'assigned_to', 'scheduled_date', 'delivered_at')
	list_filter = ('status', 'scheduled_date')
	search_fields = ('order__order_number', 'order__customer__name', 'address')

	def save_model(self, request, obj, form, change):
		super().save_model(request, obj, form, change)
		sync_order_with_delivery(obj)
