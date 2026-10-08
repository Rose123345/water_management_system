from django.contrib import admin

from accounts.admin_mixins import RecordedByAdminMixin
from .models import Customer



@admin.register(Customer)
class CustomerAdmin(RecordedByAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'customer_type', 'phone', 'user', 'status', 'created_at')
    list_filter = ('customer_type', 'status')
    search_fields = ('name', 'phone', 'email', 'user__username')
    raw_id_fields = ('user',)
