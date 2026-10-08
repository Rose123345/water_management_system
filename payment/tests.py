from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from sales.models import Order
from sales.testing import make_order, make_user

from .models import Payment


class PaymentPageTests(TestCase):
	def setUp(self):
		self.client.force_login(make_user('cashier', 'Accountant'))
		self.order = make_order(quantity=2)  # 2 x GH₵5.00

	def test_payment_list_and_form_are_reachable(self):
		self.assertEqual(self.client.get(reverse('payments:list', args=[self.order.pk])).status_code, 200)
		self.assertEqual(self.client.get(reverse('payments:add', args=[self.order.pk])).status_code, 200)

	def test_records_completed_payment_even_if_status_is_posted(self):
		response = self.client.post(reverse('payments:add', args=[self.order.pk]), {
			'amount': '4.00', 'method': Payment.Method.CASH, 'status': Payment.Status.FAILED,
		})

		self.assertRedirects(response, reverse('sales:detail', args=[self.order.pk]))
		self.assertEqual(self.order.payments.get().status, Payment.Status.COMPLETED)
		self.assertEqual(self.order.balance, Decimal('6.00'))

	def test_rejects_payment_above_balance(self):
		response = self.client.post(reverse('payments:add', args=[self.order.pk]), {
			'amount': '10.01', 'method': Payment.Method.CASH,
		})

		self.assertEqual(response.status_code, 200)
		self.assertFalse(self.order.payments.exists())

	def test_cancelled_order_cannot_take_payments(self):
		Order.objects.filter(pk=self.order.pk).update(status=Order.Status.CANCELLED)

		response = self.client.post(reverse('payments:add', args=[self.order.pk]), {
			'amount': '1.00', 'method': Payment.Method.CASH,
		})

		self.assertRedirects(response, reverse('sales:detail', args=[self.order.pk]))
		self.assertFalse(self.order.payments.exists())

	def test_roles_without_payment_access_are_denied(self):
		self.client.force_login(make_user('maker', 'Production Officer'))

		response = self.client.get(reverse('payments:add', args=[self.order.pk]))

		self.assertEqual(response.status_code, 403)
