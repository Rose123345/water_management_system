from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone

from sales.models import Order

from .models import Delivery


DELIVERY_STAFF_ROLES = ('Distribution Officer',)


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['order', 'address', 'contact_phone', 'assigned_to', 'status', 'scheduled_date', 'notes']
        widgets = {'scheduled_date': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_order = self.instance.order_id if self.instance.pk else None
        current_assignee = self.instance.assigned_to_id if self.instance.pk else None

        # Only confirmed or completed orders without a delivery can be scheduled.
        self.fields['order'].queryset = Order.objects.filter(
            Q(status__in=[Order.Status.CONFIRMED, Order.Status.COMPLETED], delivery__isnull=True)
            | Q(pk=current_order)
        ).select_related('customer')

        self.fields['assigned_to'].queryset = get_user_model().objects.filter(
            Q(is_active=True, groups__name__in=DELIVERY_STAFF_ROLES) | Q(pk=current_assignee)
        ).distinct().order_by('username')

    def save(self, commit=True):
        delivery = super().save(commit=False)
        if delivery.status == Delivery.Status.DELIVERED:
            delivery.delivered_at = delivery.delivered_at or timezone.now()
        else:
            delivery.delivered_at = None
        if commit:
            delivery.save()
        return delivery
