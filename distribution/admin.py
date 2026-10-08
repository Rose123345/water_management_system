from django.contrib import admin

from .models import Delivery


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
	list_display = ('order', 'status', 'assigned_to', 'scheduled_date', 'delivered_at')
	list_filter = ('status', 'scheduled_date')
	search_fields = ('order__order_number', 'order__customer__name', 'address')
