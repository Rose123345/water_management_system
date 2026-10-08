from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.views.decorators.http import require_POST
from accounts.permissions import ROLE_ACCESS, in_groups, role_required
from .models import Order
from .forms import OrderForm, OrderItemFormSet
from .services import advance_order_status, cancel_order, OrderStatusError

MANAGE_ROLES = ['Administrator', 'Sales Officer']

NEXT_STEP_LABELS = {
    Order.Status.PENDING: 'Confirm order',
    Order.Status.CONFIRMED: 'Mark as on the way',
    Order.Status.ON_THE_WAY: 'Mark as delivered',
}


def _error_text(error):
    if isinstance(error, ValidationError):
        return ' '.join(error.messages)
    return str(error)


@role_required(*ROLE_ACCESS['sales'])
def order_list(request):
    orders = Order.objects.select_related('customer')
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)

    return render(request, 'sales/order_list.html', {
        'orders': orders,
        'statuses': Order.Status.choices,
        'selected_status': status,
        'can_manage': in_groups(request.user, MANAGE_ROLES),
    })


@role_required(*ROLE_ACCESS['sales'])
def order_add(request):
    if not in_groups(request.user, MANAGE_ROLES):
        messages.error(request, "You don't have permission to create orders.")
        return redirect('sales:list')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.created_by = request.user
                order.save()
                formset.instance = order
                formset.save()
            messages.success(request, f"Order {order.order_number} created.")
            return redirect('sales:detail', pk=order.pk)
    else:
        form = OrderForm()
        formset = OrderItemFormSet()

    return render(request, 'sales/order_form.html', {'form': form, 'formset': formset})


@role_required(*ROLE_ACCESS['sales'])
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.select_related('customer', 'created_by'), pk=pk)
    return render(request, 'sales/order_detail.html', {
        'order': order,
        'items': order.items.select_related('product'),
        'can_manage': in_groups(request.user, MANAGE_ROLES),
        'next_step': NEXT_STEP_LABELS.get(order.status),
        'can_record_payment': (
            order.status != Order.Status.CANCELLED
            and order.balance > 0
            and in_groups(request.user, ROLE_ACCESS['payments'])
        ),
    })


@role_required(*ROLE_ACCESS['sales'])
@require_POST
def order_advance(request, pk):
    if not in_groups(request.user, MANAGE_ROLES):
        messages.error(request, "You don't have permission to change order status.")
        return redirect('sales:detail', pk=pk)

    order = get_object_or_404(Order, pk=pk)
    try:
        updated = advance_order_status(order, request.user)
    except (OrderStatusError, ValidationError) as error:
        messages.error(request, _error_text(error))
    else:
        messages.success(request, f"Order {updated.order_number} is now {updated.get_status_display()}.")
    return redirect('sales:detail', pk=pk)


@role_required(*ROLE_ACCESS['sales'])
@require_POST
def order_cancel(request, pk):
    if not in_groups(request.user, MANAGE_ROLES):
        messages.error(request, "You don't have permission to cancel orders.")
        return redirect('sales:detail', pk=pk)

    order = get_object_or_404(Order, pk=pk)
    try:
        cancel_order(order, request.user)
    except (OrderStatusError, ValidationError) as error:
        messages.error(request, _error_text(error))
    else:
        messages.success(request, f"Order {order.order_number} was cancelled.")
    return redirect('sales:detail', pk=pk)