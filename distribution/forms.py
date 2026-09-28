from django import forms

from .models import Delivery


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['order', 'address', 'contact_phone', 'assigned_to', 'status', 'scheduled_date', 'notes']
        widgets = {'scheduled_date': forms.DateInput(attrs={'type': 'date'})}