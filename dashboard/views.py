from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Sum
from django.shortcuts import render

from Inventory.models import Stock
from distribution.models import Delivery
from payment.models import Payment
from production.models import ProductionBatch
from sales.models import Order


@login_required
def dashboard(request):
    return render(request, 'dashboard/dashboard.html', {
        'order_count': Order.objects.count(),
        'recent_orders': Order.objects.select_related('customer')[:5],
        'low_stock': Stock.objects.select_related('product').filter(
            quantity_on_hand__lte=models.F('product__reorder_level')
        ),
        'payment_total': Payment.objects.filter(status=Payment.Status.COMPLETED).aggregate(total=Sum('amount'))['total'] or 0,
        'pending_deliveries': Delivery.objects.exclude(status=Delivery.Status.DELIVERED).select_related('order', 'assigned_to')[:5],
        'production_total': ProductionBatch.objects.aggregate(total=Sum('quantity_produced'))['total'] or 0,
    })
