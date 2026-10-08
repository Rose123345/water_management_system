import hashlib
import hmac
import json
from decimal import Decimal
from unittest import mock

from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.permissions import CUSTOMER_ROLE
from customers.models import Customer
from sales.models import Order
from sales.services import OrderStatusError, cancel_order
from sales.testing import make_order, make_product, make_user

from .forms import PaymentForm
from .models import Payment

SECRET = 'sk_test_wmdms'


def charge(order, amount='10.00', status='success', reference='WMDMS-ref-1', currency='GHS'):
	return {
		'status': status, 'reference': reference, 'currency': currency,
		'amount': int(Decimal(amount) * 100), 'metadata': {'order_id': order.pk},
	}


@override_settings(PAYSTACK_SECRET_KEY=SECRET, PAYSTACK_CURRENCY='GHS')
class PaystackPortalTests(TestCase):
	def setUp(self):
		self.user = make_user('ama', CUSTOMER_ROLE)
		self.customer = Customer.objects.create(
			name='Ama', phone='0241234567', email='ama@example.com', user=self.user
		)
		self.order = make_order(customer=self.customer, product=make_product(stock=50), quantity=2)  # GH₵10.00
		self.client.force_login(self.user)

	def test_order_page_offers_pay_button_for_balance(self):
		response = self.client.get(reverse('portal:order_detail', args=[self.order.pk]))

		self.assertContains(response, 'Pay GH₵10.00 now')

	@override_settings(PAYSTACK_SECRET_KEY='')
	def test_no_pay_button_when_paystack_is_not_configured(self):
		response = self.client.get(reverse('portal:order_detail', args=[self.order.pk]))

		self.assertNotContains(response, 'now</button>')

	@mock.patch('payment.paystack._call', return_value={'authorization_url': 'https://checkout.paystack.com/abc'})
	def test_pay_redirects_to_paystack_checkout_for_the_balance(self, call):
		response = self.client.post(reverse('portal:order_pay', args=[self.order.pk]))

		self.assertRedirects(response, 'https://checkout.paystack.com/abc', fetch_redirect_response=False)
		method, path, payload = call.call_args.args
		self.assertEqual((method, path), ('POST', '/transaction/initialize'))
		self.assertEqual(payload['amount'], 1000)
		self.assertEqual(payload['currency'], 'GHS')
		self.assertEqual(payload['email'], 'ama@example.com')
		self.assertEqual(payload['metadata']['order_id'], self.order.pk)
		self.assertTrue(payload['callback_url'].endswith(reverse('portal:paystack_callback')))

	def test_pay_without_email_asks_for_it(self):
		Customer.objects.filter(pk=self.customer.pk).update(email='')

		response = self.client.post(reverse('portal:order_pay', args=[self.order.pk]))

		self.assertRedirects(response, reverse('portal:profile'))

	def test_cannot_pay_someone_elses_order(self):
		other = make_order(product=self.order.items.get().product)

		response = self.client.post(reverse('portal:order_pay', args=[other.pk]))

		self.assertEqual(response.status_code, 404)

	def test_callback_records_verified_payment_once(self):
		with mock.patch('payment.paystack.verify_payment', return_value=charge(self.order)):
			url = reverse('portal:paystack_callback') + '?reference=WMDMS-ref-1'
			response = self.client.get(url)
			self.client.get(url)

		self.assertRedirects(response, reverse('portal:order_detail', args=[self.order.pk]))
		payment = self.order.payments.get()
		self.assertEqual(payment.method, Payment.Method.PAYSTACK)
		self.assertEqual(payment.amount, Decimal('10.00'))
		self.assertEqual(self.order.balance, Decimal('0.00'))

	def test_callback_ignores_failed_charge(self):
		with mock.patch('payment.paystack.verify_payment', return_value=charge(self.order, status='failed')):
			self.client.get(reverse('portal:paystack_callback') + '?reference=WMDMS-ref-1')

		self.assertFalse(self.order.payments.exists())

	def test_callback_rejects_wrong_currency(self):
		with mock.patch('payment.paystack.verify_payment', return_value=charge(self.order, currency='NGN')):
			self.client.get(reverse('portal:paystack_callback') + '?reference=WMDMS-ref-1')

		self.assertFalse(self.order.payments.exists())

	def test_paid_pending_order_cannot_be_cancelled(self):
		Payment.objects.create(order=self.order, amount='10.00', method=Payment.Method.PAYSTACK, reference='r')

		with self.assertRaises(OrderStatusError):
			cancel_order(self.order, self.user)
		self.order.refresh_from_db()
		self.assertEqual(self.order.status, Order.Status.PENDING)


@override_settings(PAYSTACK_SECRET_KEY=SECRET, PAYSTACK_CURRENCY='GHS')
class PaystackWebhookTests(TestCase):
	def setUp(self):
		self.order = make_order(quantity=2)

	def post(self, body, signature=None):
		raw = json.dumps(body).encode()
		signature = signature or hmac.new(SECRET.encode(), raw, hashlib.sha512).hexdigest()
		return self.client.post(
			reverse('payments:paystack_webhook'), raw, content_type='application/json',
			headers={'X-Paystack-Signature': signature},
		)

	def test_signed_charge_success_records_payment_once(self):
		body = {'event': 'charge.success', 'data': charge(self.order, amount='4.00')}

		self.assertEqual(self.post(body).status_code, 200)
		self.assertEqual(self.post(body).status_code, 200)

		self.assertEqual(self.order.payments.get().amount, Decimal('4.00'))

	def test_bad_signature_is_rejected(self):
		response = self.post({'event': 'charge.success', 'data': charge(self.order)}, signature='forged')

		self.assertEqual(response.status_code, 400)
		self.assertFalse(self.order.payments.exists())


class PaystackClientTests(TestCase):
	@override_settings(PAYSTACK_SECRET_KEY=SECRET)
	def test_requests_send_key_and_a_user_agent(self):
		response = mock.MagicMock()
		response.__enter__.return_value.read.return_value = b'{"status": true, "data": {"status": "success"}}'
		with mock.patch('payment.paystack.urlopen', return_value=response) as urlopen:
			from . import paystack
			self.assertEqual(paystack.verify_payment('ref-1'), {'status': 'success'})

		request = urlopen.call_args.args[0]
		self.assertEqual(request.full_url, 'https://api.paystack.co/transaction/verify/ref-1')
		self.assertEqual(request.get_header('Authorization'), f'Bearer {SECRET}')
		self.assertEqual(request.get_header('User-agent'), 'WMDMS/1.0')


class StaffPaymentFormTests(TestCase):
	def test_staff_cannot_record_paystack_payments_by_hand(self):
		methods = [value for value, _ in PaymentForm().fields['method'].choices]

		self.assertNotIn(Payment.Method.PAYSTACK, methods)
		self.assertIn(Payment.Method.CASH, methods)
