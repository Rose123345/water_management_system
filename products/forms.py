from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'product_type', 'package_size', 'unit_price', 'reorder_level', 'description', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_unit_price(self):
        price = self.cleaned_data['unit_price']
        if price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")
        return price

    def clean_reorder_level(self):
        level = self.cleaned_data['reorder_level']
        if level < 0:
            raise forms.ValidationError("Reorder level cannot be negative.")
        return level