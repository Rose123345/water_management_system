from django.contrib import admin
from .models import Product

# Register your models here.


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_type', 'package_size', 'unit_price', 'reorder_level', 'status')
    list_filter = ('product_type', 'status')
    search_fields = ('name', 'package_size')