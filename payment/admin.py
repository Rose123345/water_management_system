from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
	list_display = ('order', 'amount', 'method', 'status', 'payment_date', 'received_by')
	list_filter = ('method', 'status', 'payment_date')
	search_fields = ('order__order_number', 'reference')
from django.contrib import admin

# Register your models here.
