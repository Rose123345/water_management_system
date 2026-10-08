from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from accounts.permissions import customer_required
from Inventory.services import products_with_stock
from payment import paystack
from products.models import Product
from sales.forms import CustomerOrderItemFormSet
from sales.models import Order
from sales.services import OrderStatusError, cancel_order

from .forms import CustomerProfileForm
from .models import Customer


def _customer_orders(customer):
    return customer.orders.select_related('delivery').prefetch_related('items', 'payments')


@customer_required
def portal_home(request):
    customer = request.user.customer_profile
    return render(request, 'portal/home.html', {
        'customer': customer,
        'orders': _customer_orders(customer),
    })


@customer_required
def portal_products(request):
    products = products_with_stock().filter(status=Product.Status.ACTIVE).order_by('product_type', 'name')
    for product in products:
        if product.stock_quantity <= 0:
            product.availability = 'Out of stock'
        elif product.stock_quantity <= product.reorder_level:
            product.availability = 'Low stock'
        else:
            product.availability = 'In stock'
    return render(request, 'portal/products.html', {'products': products})


@customer_required
def portal_order_create(request):
    customer = request.user.customer_profile
    if customer.status != Customer.Status.ACTIVE:
        messages.error(request, 'Your account is inactive. Please contact us to place an order.')
        return redirect('portal:home')

    order = Order(customer=customer, created_by=request.user)
    # "Order" buttons on the products page pre-select that product in the first row.
    initial = [{'product': request.GET['product']}] if request.GET.get('product', '').isdigit() else None
    formset = CustomerOrderItemFormSet(request.POST or None, instance=order, initial=initial)
    if request.method == 'POST' and formset.is_valid():
        with transaction.atomic():
            order.save()
            formset.instance = order
            formset.save()
        messages.success(
            request,
            f'Order {order.order_number} was placed. Our sales team will confirm it shortly.',
        )
        return redirect('portal:order_detail', pk=order.pk)

    return render(request, 'portal/order_form.html', {
        'formset': formset,
        'product_prices': {
            str(pk): str(price) for pk, price in
            Product.objects.filter(status=Product.Status.ACTIVE).values_list('pk', 'unit_price')
        },
    })


@customer_required
def portal_order_detail(request, pk):
    customer = request.user.customer_profile
    order = get_object_or_404(_customer_orders(customer), pk=pk)
    return render(request, 'portal/order_detail.html', {
        'order': order,
        'items': order.items.select_related('product'),
        'payments': order.payments.filter(status='completed'),
        'delivery': getattr(order, 'delivery', None),
        'can_pay_online': _can_pay_online(order),
    })


@customer_required
@require_POST
def portal_order_cancel(request, pk):
    customer = request.user.customer_profile
    order = get_object_or_404(Order, pk=pk, customer=customer)
    if order.status != Order.Status.PENDING:
        messages.error(request, 'Only pending orders can be cancelled. Please contact us about confirmed orders.')
    else:
        try:
            cancel_order(order, request.user)
        except OrderStatusError as error:
            messages.error(request, str(error))
        else:
            messages.success(request, f'Order {order.order_number} was cancelled.')
    return redirect('portal:order_detail', pk=pk)


@customer_required(require_profile=False)
def portal_profile(request):
    customer = getattr(request.user, 'customer_profile', None)
    creating = customer is None
    if creating:
        customer = Customer(
            user=request.user,
            created_by=request.user,
            name=request.user.get_full_name(),
            email=request.user.email,
        )

    form = CustomerProfileForm(request.POST or None, instance=customer)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Your details were saved.')
        return redirect('portal:home')

    return render(request, 'portal/profile_form.html', {'form': form, 'creating': creating})


def _can_pay_online(order):
    return paystack.is_configured() and order.status != Order.Status.CANCELLED and order.balance > 0


@customer_required
@require_POST
def portal_order_pay(request, pk):
    customer = request.user.customer_profile
    order = get_object_or_404(Order, pk=pk, customer=customer)
    if not _can_pay_online(order):
        messages.error(request, 'This order cannot be paid online right now.')
        return redirect('portal:order_detail', pk=pk)

    email = customer.email or request.user.email
    if not email:
        messages.error(request, 'Please add your email address before paying online. Paystack sends your receipt there.')
        return redirect('portal:profile')

    try:
        checkout_url = paystack.initialize_payment(
            order, email, request.build_absolute_uri(reverse('portal:paystack_callback'))
        )
    except paystack.PaystackError as error:
        messages.error(request, f'Online payment is unavailable: {error}')
        return redirect('portal:order_detail', pk=pk)
    return redirect(checkout_url)


@customer_required
def portal_paystack_callback(request):
    """Paystack sends the customer back here; verify with Paystack before recording anything."""
    reference = request.GET.get('reference', '')
    if not reference:
        return redirect('portal:home')

    try:
        payment = paystack.record_successful_payment(paystack.verify_payment(reference))
    except paystack.PaystackError as error:
        messages.error(request, f'We could not confirm your payment: {error}')
        return redirect('portal:home')

    if payment is None:
        messages.error(request, 'Your payment was not completed. You have not been charged.')
        return redirect('portal:home')

    messages.success(request, f'Payment of GH₵{payment.amount:.2f} received. Thank you!')
    if payment.order.customer_id == request.user.customer_profile.pk:
        return redirect('portal:order_detail', pk=payment.order_id)
    return redirect('portal:home')
