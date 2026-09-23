from django import forms
from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'customer_type', 'phone', 'email', 'address', 'status']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        digits = phone.replace(' ', '').replace('-', '')
        if not digits.isdigit() or len(digits) < 9:
            raise forms.ValidationError("Enter a valid phone number.")
        return phone