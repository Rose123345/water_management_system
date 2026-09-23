from django.contrib import admin
from .models import Customer


# Register your models here.


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'customer_type', 'phone', 'status', 'created_at')
    list_filter = ('customer_type', 'status')
    search_fields = ('name', 'phone', 'email')
