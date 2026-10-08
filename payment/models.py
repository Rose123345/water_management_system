from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Payment(models.Model):
	class Method(models.TextChoices):
		CASH = 'cash', 'Cash'
		MOBILE_MONEY = 'mobile_money', 'Mobile money'
		BANK_TRANSFER = 'bank_transfer', 'Bank transfer'
		CARD = 'card', 'Card'

	class Status(models.TextChoices):
		PENDING = 'pending', 'Pending'
		COMPLETED = 'completed', 'Completed'
		FAILED = 'failed', 'Failed'

	order = models.ForeignKey(
		'sales.Order', on_delete=models.PROTECT, related_name='payments'
	)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	method = models.CharField(max_length=20, choices=Method.choices)
	status = models.CharField(max_length=10, choices=Status.choices, default=Status.COMPLETED)
	reference = models.CharField(max_length=100, blank=True)
	payment_date = models.DateTimeField(auto_now_add=True)
	received_by = models.ForeignKey(
		settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
		null=True, blank=True, related_name='payments_received'
	)

	class Meta:
		ordering = ['-payment_date', '-pk']

	def __str__(self):
		return f'{self.order.order_number} - {self.amount}'

	def clean(self):
		if self.amount is None:
			return
		if self.amount <= 0:
			raise ValidationError({'amount': 'Payment amount must be greater than zero.'})
		if self.status == self.Status.COMPLETED and self.order_id:
			other_payments = self.order.payments.filter(
				status=self.Status.COMPLETED
			).exclude(pk=self.pk)
			if self.amount > self.order.total - sum(
				payment.amount for payment in other_payments
			):
				raise ValidationError({'amount': 'Payment cannot exceed the order balance.'})

	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)
