from django import forms
from .models import ProductionBatch


class ProductionBatchForm(forms.ModelForm):
    class Meta:
        model = ProductionBatch
        fields = ['batch_number', 'product', 'production_date', 'quantity_produced']
        widgets = {
            'production_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_quantity_produced(self):
        quantity = self.cleaned_data['quantity_produced']
        if quantity <= 0:
            raise forms.ValidationError('Quantity produced must be greater than zero.')
        return quantity