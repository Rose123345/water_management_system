from django.db import models
from django.conf import settings


class Stock(models.Model):
	product = models.OneToOneField(
		'products.Product',
		on_delete=models.CASCADE,
		related_name='stock',
	)
	quantity_on_hand = models.PositiveIntegerField(default=0)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f'{self.product}: {self.quantity_on_hand}'


class StockMovement(models.Model):
	class MovementType(models.TextChoices):
		RECEIPT = 'receipt', 'Stock receipt'
		ISSUE = 'issue', 'Stock issue'
		PRODUCTION = 'production', 'Production'

	product = models.ForeignKey(
		'products.Product',
		on_delete=models.PROTECT,
		related_name='stock_movements',
	)
	movement_type = models.CharField(max_length=12, choices=MovementType.choices)
	quantity = models.PositiveIntegerField()
	note = models.CharField(max_length=255, blank=True)
	production_batch = models.OneToOneField(
		'production.ProductionBatch',
		on_delete=models.PROTECT,
		null=True,
		blank=True,
		related_name='stock_movement',
	)
	recorded_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='stock_movements_recorded',
	)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at', '-pk']

	def __str__(self):
		return f'{self.get_movement_type_display()}: {self.product} x {self.quantity}'
