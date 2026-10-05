from django.db.models import Sum
from django.shortcuts import render
from accounts.permissions import ROLE_ACCESS, role_required

from Inventory.models import Stock, StockMovement
from distribution.models import Delivery
from payment.models import Payment
from production.models import ProductionBatch
from sales.models import Order


@role_required(*ROLE_ACCESS['reports'])
def report_index(request):
    orders = Order.objects.exclude(status=Order.Status.CANCELLED).prefetch_related('items')
    sales_total = sum(order.total for order in orders)
    return render(request, 'reports/report_index.html', {
        'sales_total': sales_total,
        'production_total': ProductionBatch.objects.aggregate(total=Sum('quantity_produced'))['total'] or 0,
        'inventory_movements': StockMovement.objects.select_related('product')[:20],
        'payment_total': Payment.objects.filter(status=Payment.Status.COMPLETED).aggregate(total=Sum('amount'))['total'] or 0,
        'deliveries': Delivery.objects.select_related('order', 'assigned_to'),
        'stock': Stock.objects.select_related('product'),
    })
