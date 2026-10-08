from django.conf import settings
from django.db import models
from django.utils import timezone


class ExpenseCategory(models.Model):
	name = models.CharField(max_length=100, unique=True)
	description = models.TextField(blank=True)

	class Meta:
		ordering = ['name']

	def __str__(self):
		return self.name


class Expense(models.Model):
	category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT, related_name='expenses')
	description = models.CharField(max_length=255)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	expense_date = models.DateField(default=timezone.localdate)
	recorded_by = models.ForeignKey(
		settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
		null=True, blank=True, related_name='expenses_recorded'
	)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-expense_date', '-created_at']

	def __str__(self):
		return f'{self.description} - {self.amount}'
