from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from Inventory.services import products_with_stock
from products.models import Product

from .models import Order, OrderItem


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer']


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(
            status=Product.Status.ACTIVE
        ).order_by('name')

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity <= 0:
            raise forms.ValidationError('Quantity must be greater than zero.')
        return quantity


OrderItemFormSet = inlineformset_factory(
    Order, OrderItem, form=OrderItemForm, extra=1, can_delete=True
)

class CustomerOrderItemForm(OrderItemForm):
    """Portal order line: product dropdown shows price and availability."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = products_with_stock().filter(
            status=Product.Status.ACTIVE
        ).order_by('name')
        self.fields['product'].label_from_instance = self.product_label
        self.fields['quantity'].widget.attrs.update({'min': 1})

    @staticmethod
    def product_label(product):
        label = f'{product} - GH₵{product.unit_price:.2f}'
        if product.stock_quantity <= 0:
            label += ' (out of stock)'
        return label


class BaseCustomerOrderItemFormSet(BaseInlineFormSet):
    def clean(self):
        chosen = set()
        for form in self.forms:
            product = form.cleaned_data.get('product') if hasattr(form, 'cleaned_data') else None
            if product is None:
                continue
            if product in chosen:
                raise forms.ValidationError(
                    f'You picked {product} more than once. Put the total quantity on one line instead.'
                )
            chosen.add(product)
        super().clean()


# Customers place orders from the portal and add product rows as they need them.
CustomerOrderItemFormSet = inlineformset_factory(
    Order, OrderItem, form=CustomerOrderItemForm, formset=BaseCustomerOrderItemFormSet,
    extra=0, min_num=1, validate_min=True, max_num=50, validate_max=True, can_delete=False,
)
