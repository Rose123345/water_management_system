from django.db import models
from django.conf import settings
from django.utils import timezone


class ProductionBatch(models.Model):
	batch_number = models.CharField(max_length=50, unique=True)
	product = models.ForeignKey(
		'products.Product',
		on_delete=models.PROTECT,
		related_name='production_batches',
	)
	production_date = models.DateField(default=timezone.localdate)
	quantity_produced = models.PositiveIntegerField()
	recorded_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='production_batches_recorded',
	)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-production_date', '-created_at']

	def __str__(self):
		return f'{self.batch_number} - {self.product.name}'
