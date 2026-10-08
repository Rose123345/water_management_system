"""Paystack checkout: start a transaction, verify it, and record the payment once."""
import hashlib
import hmac
import json
import uuid
from decimal import Decimal
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.db import transaction

from sales.models import Order

from .models import Payment


API_BASE = 'https://api.paystack.co'


class PaystackError(Exception):
	pass


def is_configured():
	return bool(settings.PAYSTACK_SECRET_KEY)


def _call(method, path, payload=None):
	request = Request(
		API_BASE + path,
		data=json.dumps(payload).encode() if payload is not None else None,
		method=method,
		headers={
			'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
			'Content-Type': 'application/json',
			# Paystack's firewall rejects Python's default User-Agent (Cloudflare error 1010).
			'User-Agent': 'WMDMS/1.0',
		},
	)
	try:
		with urlopen(request, timeout=20) as response:
			body = json.load(response)
	except HTTPError as error:
		try:
			message = json.load(error).get('message')
		except ValueError:
			message = None
		raise PaystackError(message or f'Paystack returned HTTP {error.code}.') from error
	except (URLError, TimeoutError, ValueError) as error:
		raise PaystackError('Could not reach Paystack. Please try again.') from error
	if not body.get('status'):
		raise PaystackError(body.get('message') or 'Paystack rejected the request.')
	return body['data']


def to_subunit(amount):
	"""Paystack amounts are in the currency's smallest unit (pesewas for GHS)."""
	return int((Decimal(amount) * 100).quantize(Decimal('1')))


def initialize_payment(order, email, callback_url):
	"""Start a Paystack checkout for the order's balance and return the checkout URL."""
	reference = f'WMDMS-{order.pk}-{uuid.uuid4().hex[:12]}'
	data = _call('POST', '/transaction/initialize', {
		'email': email,
		'amount': to_subunit(order.balance),
		'currency': settings.PAYSTACK_CURRENCY,
		'reference': reference,
		'callback_url': callback_url,
		'metadata': {'order_id': order.pk, 'order_number': order.order_number},
	})
	return data['authorization_url']


def verify_payment(reference):
	return _call('GET', f'/transaction/verify/{reference}')


def is_valid_signature(body, signature):
	expected = hmac.new(settings.PAYSTACK_SECRET_KEY.encode(), body, hashlib.sha512).hexdigest()
	return bool(signature) and hmac.compare_digest(expected, signature)


@transaction.atomic
def record_successful_payment(data):
	"""Record a verified Paystack charge. Safe to call more than once for the same reference.

	Returns the Payment, or None when the charge was not successful.
	"""
	if data.get('status') != 'success':
		return None
	if data.get('currency') != settings.PAYSTACK_CURRENCY:
		raise PaystackError('Unexpected payment currency.')

	order_id = (data.get('metadata') or {}).get('order_id')
	order = Order.objects.select_for_update().filter(pk=order_id).first()
	if order is None:
		raise PaystackError('Payment does not match an order.')

	reference = data['reference']
	existing = order.payments.filter(reference=reference, method=Payment.Method.PAYSTACK).first()
	if existing:
		return existing

	return Payment.objects.create(
		order=order,
		amount=Decimal(data['amount']) / 100,
		method=Payment.Method.PAYSTACK,
		status=Payment.Status.COMPLETED,
		reference=reference,
	)
