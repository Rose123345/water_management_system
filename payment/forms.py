from django import forms

from .models import Payment


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'method', 'reference']

    def __init__(self, *args, order=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.order = order
        # Paystack payments are only recorded automatically after Paystack confirms them.
        self.fields['method'].choices = [
            choice for choice in self.fields['method'].choices if choice[0] != Payment.Method.PAYSTACK
        ]

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if self.order and amount > self.order.balance:
            raise forms.ValidationError('Payment cannot exceed the order balance.')
        return amount