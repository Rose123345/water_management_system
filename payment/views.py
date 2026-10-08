from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
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
	if order.status == Order.Status.CANCELLED:
		messages.error(request, 'Payments cannot be recorded against a cancelled order.')
		return redirect('sales:detail', pk=order.pk)

	if request.method == 'POST':
		form = PaymentForm(request.POST, order=order)
		if form.is_valid():
			try:
				with transaction.atomic():
					# Lock the order so two payments recorded at the same time
					# cannot together exceed the outstanding balance.
					locked_order = Order.objects.select_for_update().get(pk=order.pk)
					payment = form.save(commit=False)
					payment.order = locked_order
					payment.status = Payment.Status.COMPLETED
					payment.received_by = request.user
					payment.save()
			except ValidationError as error:
				form.add_error(None, error)
			else:
				messages.success(request, 'Payment recorded.')
				return redirect('sales:detail', pk=order.pk)
	else:
		form = PaymentForm(order=order)
	return render(request, 'payment/payment_form.html', {'form': form, 'order': order})
