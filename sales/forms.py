from django import forms
from django.forms import inlineformset_factory

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

# Customers place orders from the portal; they need at least one item and a few blank rows.
CustomerOrderItemFormSet = inlineformset_factory(
    Order, OrderItem, form=OrderItemForm, extra=2, min_num=1, validate_min=True, can_delete=False
)
