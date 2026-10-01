from django.db import models
from django.conf import settings


class Product(models.Model):
    class ProductType(models.TextChoices):
        BOTTLED = 'bottled', 'Bottled Water'
        SACHET = 'sachet', 'Sachet Water'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'

    name = models.CharField(max_length=150)
    product_type = models.CharField(max_length=10, choices=ProductType.choices)
    package_size = models.CharField(
        max_length=30,
        help_text="e.g. 500ml, 750ml, 1.5L, 30 sachets/bag"
    )
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_level = models.PositiveIntegerField(
        default=50,
        help_text="Stock falls below this to trigger a low-stock warning"
    )
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='products_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['product_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.package_size})"