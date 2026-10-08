from django import forms
from .models import Customer


def validate_phone(phone):
    digits = phone.replace(' ', '').replace('-', '').removeprefix('+')
    if not digits.isdigit() or len(digits) < 9:
        raise forms.ValidationError("Enter a valid phone number.")
    return phone


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'customer_type', 'phone', 'email', 'address', 'status']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_phone(self):
        return validate_phone(self.cleaned_data['phone'])


class CustomerProfileForm(forms.ModelForm):
    """Details a customer can edit about themselves in the customer portal."""

    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'address']
        labels = {'name': 'Full name or business name'}
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_phone(self):
        return validate_phone(self.cleaned_data['phone'])