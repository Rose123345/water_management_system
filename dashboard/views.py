from django.db.models import Sum
from django.shortcuts import render

from Inventory.services import low_stock_products
from distribution.models import Delivery
from payment.models import Payment
from production.models import ProductionBatch
from sales.models import Order
from accounts.permissions import ROLE_ACCESS, role_required


@role_required(*ROLE_ACCESS['dashboard'])
def dashboard(request):
    low_stock = low_stock_products()
    return render(request, 'dashboard/dashboard.html', {
        'order_count': Order.objects.count(),
        'recent_orders': Order.objects.select_related('customer')[:5],
        'low_stock': low_stock[:5],
        'payment_total': Payment.objects.filter(status=Payment.Status.COMPLETED).aggregate(total=Sum('amount'))['total'] or 0,
        'pending_deliveries': Delivery.objects.exclude(status=Delivery.Status.DELIVERED).select_related('order', 'assigned_to')[:5],
        'pending_delivery_count': Delivery.objects.exclude(status=Delivery.Status.DELIVERED).count(),
        'low_stock_count': low_stock.count(),
        'production_total': ProductionBatch.objects.aggregate(total=Sum('quantity_produced'))['total'] or 0,
    })
