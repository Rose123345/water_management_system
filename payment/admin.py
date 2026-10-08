from django.contrib import admin

from accounts.admin_mixins import RecordedByAdminMixin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(RecordedByAdminMixin, admin.ModelAdmin):
	recorded_by_field = 'received_by'
	list_display = ('order', 'amount', 'method', 'status', 'payment_date', 'received_by')
	list_filter = ('method', 'status', 'payment_date')
	search_fields = ('order__order_number', 'reference')
