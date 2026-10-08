import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction


class Order(models.Model):
	class Status(models.TextChoices):
		PENDING = 'pending', 'Pending'
		CONFIRMED = 'confirmed', 'Confirmed'
		ON_THE_WAY = 'on_the_way', 'On the way'
		DELIVERED = 'delivered', 'Delivered'
		CANCELLED = 'cancelled', 'Cancelled'

	order_number = models.CharField(max_length=20, unique=True, editable=False)
	customer = models.ForeignKey(
		'customers.Customer', on_delete=models.PROTECT, related_name='orders'
	)
	status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
	created_by = models.ForeignKey(
		settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
		null=True, blank=True, related_name='orders_created'
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-created_at', '-pk']

	def save(self, *args, **kwargs):
		if self.order_number:
			super().save(*args, **kwargs)
			return
		# Number from the primary key so concurrent saves or deleted orders
		# can never produce a duplicate order number.
		with transaction.atomic():
			self.order_number = f'TMP-{uuid.uuid4().hex[:16]}'
			super().save(*args, **kwargs)
			self.order_number = f'ORD-{self.pk:06d}'
			super().save(update_fields=['order_number'])

	def __str__(self):
		return self.order_number

	@property
	def subtotal(self):
		return sum((item.line_total for item in self.items.all()), Decimal('0.00'))

	@property
	def total(self):
		return self.subtotal

	@property
	def amount_paid(self):
		return sum((payment.amount for payment in self.payments.filter(
			status='completed'
		)), Decimal('0.00'))

	@property
	def balance(self):
		return max(self.total - self.amount_paid, Decimal('0.00'))


class OrderItem(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
	product = models.ForeignKey(
		'products.Product', on_delete=models.PROTECT, related_name='order_items'
	)
	quantity = models.PositiveIntegerField()
	unit_price = models.DecimalField(max_digits=10, decimal_places=2)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['order', 'product'], name='unique_order_product'),
		]

	@property
	def line_total(self):
		return self.unit_price * self.quantity

	def clean(self):
		# Order forms only ask for product and quantity; price comes from the product.
		if self.unit_price is None and self.product_id:
			self.unit_price = self.product.unit_price
		if self.quantity is not None and self.quantity <= 0:
			raise ValidationError({'quantity': 'Quantity must be greater than zero.'})
		if self.unit_price is not None and self.unit_price <= 0:
			raise ValidationError({'unit_price': 'Unit price must be greater than zero.'})

	def save(self, *args, **kwargs):
		if not self.unit_price and self.product_id:
			self.unit_price = self.product.unit_price
		self.full_clean()
		super().save(*args, **kwargs)
