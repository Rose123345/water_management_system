from django import forms
from .models import StockMovement


class StockMovementForm(forms.ModelForm):
    movement_type = forms.ChoiceField(choices=[
        (StockMovement.MovementType.RECEIPT, 'Stock receipt'),
        (StockMovement.MovementType.ISSUE, 'Stock issue'),
    ])

    class Meta:
        model = StockMovement
        fields = ['product', 'movement_type', 'quantity', 'note']
        widgets = {
            'note': forms.TextInput(attrs={'maxlength': 255}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity <= 0:
            raise forms.ValidationError('Movement quantity must be greater than zero.')
        return quantity