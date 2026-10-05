from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from accounts.permissions import ROLE_ACCESS, role_required

from sales.models import Order

from .forms import PaymentForm
from .models import Payment


@role_required(*ROLE_ACCESS['payments'])
def payment_list(request, order_pk):
	order = get_object_or_404(Order, pk=order_pk)
	payments = order.payments.all()
	return render(request, 'payment/payment_list.html', {'order': order, 'payments': payments})


@role_required(*ROLE_ACCESS['payments'])
def payment_create(request, order_pk):
	order = get_object_or_404(Order, pk=order_pk)
	if request.method == 'POST':
		form = PaymentForm(request.POST, order=order)
		if form.is_valid():
			payment = form.save(commit=False)
			payment.order = order
			payment.received_by = request.user
			payment.save()
			messages.success(request, 'Payment recorded.')
			return redirect('sales:detail', pk=order.pk)
	else:
		form = PaymentForm(order=order)
	return render(request, 'payment/payment_form.html', {'form': form, 'order': order})
from django.shortcuts import render

# Create your views here.
