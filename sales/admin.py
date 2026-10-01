
from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = ('product', 'quantity', 'unit_price', 'line_total')

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'created_at', 'status', 'display_total')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__name',)
    # Status is read-only here so nobody can skip the stock deduction by editing it in admin
    readonly_fields = ('status', 'display_total', 'created_by')
    inlines = [OrderItemInline]

    @admin.display(description='Total')
    def display_total(self, obj):
        return obj.total
