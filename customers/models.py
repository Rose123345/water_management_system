from django.db import models
from django.conf import settings


# Create your models here.



class Customer(models.Model):
    class CustomerType(models.TextChoices):
        INDIVIDUAL = 'individual', 'Individual'
        RETAILER = 'retailer', 'Retailer'
        SHOP = 'shop', 'Shop'
        BUSINESS = 'business', 'Business'
        DISTRIBUTOR = 'distributor', 'Distributor'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'

    name = models.CharField(max_length=150)
    customer_type = models.CharField(
        max_length=20, choices=CustomerType.choices, default=CustomerType.INDIVIDUAL
    )
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='customers_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name