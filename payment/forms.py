from django import forms

from .models import Payment


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'method', 'reference', 'status']
        widgets = {'status': forms.HiddenInput()}

    def __init__(self, *args, order=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.order = order
        self.initial.setdefault('status', Payment.Status.COMPLETED)

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if self.order and amount > self.order.balance:
            raise forms.ValidationError('Payment cannot exceed the order balance.')
        return amount