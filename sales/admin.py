from django import forms
from django.contrib import admin

from .models import Order, OrderItem


class OrderItemAdminForm(forms.ModelForm):
    unit_price = forms.DecimalField(required=False, max_digits=10, decimal_places=2)

    class Meta:
        model = OrderItem
        fields = ('product', 'quantity', 'unit_price')

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        if product and cleaned_data.get('unit_price') is None:
            cleaned_data['unit_price'] = product.unit_price
        return cleaned_data


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    form = OrderItemAdminForm
    fields = ('product', 'quantity', 'unit_price', 'display_line_total')
    readonly_fields = ('display_line_total',)
    extra = 1
    can_delete = False

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status != Order.Status.DRAFT:
            return ('product', 'quantity', 'unit_price', 'line_total')
        return self.readonly_fields

    def has_add_permission(self, request, obj=None):
        return obj is None or obj.status == Order.Status.DRAFT

    def has_delete_permission(self, request, obj=None):
        return obj is None or obj.status == Order.Status.DRAFT

    @admin.display(description='Line total')
    def display_line_total(self, obj):
        if not obj or not obj.quantity or not obj.unit_price:
            return '-'
        return obj.line_total


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'created_at', 'status', 'display_total')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__name',)
    readonly_fields = ('order_number', 'status', 'display_total', 'created_by')
    inlines = [OrderItemInline]

    def get_fields(self, request, obj=None):
        if obj is None:
            return ('customer', 'status', 'display_total', 'created_by')
        return ('order_number', 'customer', 'status', 'display_total', 'created_by', 'created_at', 'updated_at')

    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj:
            readonly.extend(('created_at', 'updated_at'))
        return tuple(readonly)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    @admin.display(description='Total')
    def display_total(self, obj):
        return obj.total if obj.pk else 'Calculated from order items after saving'
