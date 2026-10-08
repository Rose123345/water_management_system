from django.contrib import admin

from accounts.admin_mixins import RecordedByAdminMixin

from .models import Product


@admin.register(Product)
class ProductAdmin(RecordedByAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'product_type', 'package_size', 'unit_price', 'reorder_level', 'status')
    list_filter = ('product_type', 'status')
    search_fields = ('name', 'package_size')