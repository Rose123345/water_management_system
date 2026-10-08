import json
import logging

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from accounts.permissions import ROLE_ACCESS, role_required

from sales.models import Order

from . import paystack
from .forms import PaymentForm
from .models import Payment

logger = logging.getLogger(__name__)


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


@csrf_exempt
@require_POST
def paystack_webhook(request):
	"""Paystack calls this after a charge, so payments are recorded even if the customer never returns."""
	if not paystack.is_valid_signature(request.body, request.headers.get('X-Paystack-Signature')):
		return HttpResponseBadRequest('Invalid signature')
	try:
		event = json.loads(request.body)
	except ValueError:
		return HttpResponseBadRequest('Invalid JSON')
	if event.get('event') == 'charge.success':
		try:
			paystack.record_successful_payment(event.get('data') or {})
		except paystack.PaystackError:
			logger.exception('Could not record Paystack webhook payment')
	return HttpResponse(status=200)
