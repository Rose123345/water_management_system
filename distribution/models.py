from django.conf import settings
from django.db import models
from django.utils import timezone


class Delivery(models.Model):
	class Status(models.TextChoices):
		PENDING = 'pending', 'Pending'
		ASSIGNED = 'assigned', 'Assigned'
		OUT_FOR_DELIVERY = 'out_for_delivery', 'Out for delivery'
		DELIVERED = 'delivered', 'Delivered'
		FAILED = 'failed', 'Failed'

	order = models.OneToOneField('sales.Order', on_delete=models.PROTECT, related_name='delivery')
	address = models.TextField()
	contact_phone = models.CharField(max_length=20, blank=True)
	assigned_to = models.ForeignKey(
		settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
		null=True, blank=True, related_name='deliveries_assigned'
	)
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
	scheduled_date = models.DateField(default=timezone.localdate)
	delivered_at = models.DateTimeField(null=True, blank=True)
	notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['scheduled_date', '-created_at']

	def __str__(self):
		return f'{self.order.order_number} - {self.get_status_display()}'
