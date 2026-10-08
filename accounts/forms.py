from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.db import transaction

from customers.forms import validate_phone
from customers.models import Customer

from .permissions import CUSTOMER_ROLE


class CustomerRegistrationForm(UserCreationForm):
    """Public sign-up: creates a login with the Customer role and its customer record."""

    full_name = forms.CharField(max_length=150, label='Full name or business name')
    phone = forms.CharField(max_length=20, label='Phone number')
    email = forms.EmailField(required=False, label='Email (optional)')
    address = forms.CharField(
        required=False, label='Delivery address (optional)',
        widget=forms.Textarea(attrs={'rows': 3}),
    )

    field_order = ['full_name', 'username', 'phone', 'email', 'address', 'password1', 'password2']

    class Meta(UserCreationForm.Meta):
        fields = ('username',)

    def clean_phone(self):
        return validate_phone(self.cleaned_data['phone'])

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.save()
        customer_group, _ = Group.objects.get_or_create(name=CUSTOMER_ROLE)
        user.groups.add(customer_group)
        Customer.objects.create(
            user=user,
            name=self.cleaned_data['full_name'],
            phone=self.cleaned_data['phone'],
            email=self.cleaned_data['email'],
            address=self.cleaned_data['address'],
            created_by=user,
        )
        return user
