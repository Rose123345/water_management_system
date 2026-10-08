from decimal import Decimal

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from customers.models import Customer
from distribution.models import Delivery
from Inventory.models import Stock
from payment.models import Payment

from .models import Order
from .services import OrderStatusError, advance_order_status, cancel_order, sync_order_with_delivery
from .testing import make_order, make_product, make_user


class OrderNumberTests(TestCase):
	def test_order_numbers_stay_unique_after_an_order_is_deleted(self):
		first = make_order()
		product = first.items.get().product
		second = make_order(customer=first.customer, product=product)
		second.items.all().delete()
		second.delete()

		third = make_order(customer=first.customer, product=product)

		self.assertNotEqual(first.order_number, third.order_number)
		self.assertEqual(third.order_number, f'ORD-{third.pk:06d}')


class OrderPageTests(TestCase):
	def setUp(self):
		self.client.force_login(make_user('seller', 'Sales Officer'))

	def test_staff_can_create_order_from_the_order_form(self):
		product = make_product(price='4.25')
		customer = Customer.objects.create(name='Form Customer', phone='0240000001')

		response = self.client.post(reverse('sales:add'), {
			'customer': customer.pk,
			'items-TOTAL_FORMS': '1', 'items-INITIAL_FORMS': '0',
			'items-MIN_NUM_FORMS': '0', 'items-MAX_NUM_FORMS': '1000',
			'items-0-product': product.pk, 'items-0-quantity': '4',
		})

		order = Order.objects.get(customer=customer)
		self.assertRedirects(response, reverse('sales:detail', args=[order.pk]))
		self.assertEqual(order.items.get().unit_price, Decimal('4.25'))

	def test_order_detail_with_balance_links_to_record_payment(self):
		order = make_order()

		response = self.client.get(reverse('sales:detail', args=[order.pk]))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, reverse('payments:add', args=[order.pk]))

	def test_confirmed_order_offers_complete_and_cancel(self):
		order = make_order(status=Order.Status.CONFIRMED)

		response = self.client.get(reverse('sales:detail', args=[order.pk]))

		self.assertContains(response, 'Mark as on the way')
		self.assertContains(response, 'Cancel order')

	def test_failed_status_change_shows_readable_message(self):
		order = make_order(product=make_product(stock=1), quantity=5)

		response = self.client.post(reverse('sales:advance', args=[order.pk]), follow=True)

		messages = [str(message) for message in get_messages(response.wsgi_request)]
		self.assertIn('Cannot issue more stock than is currently available.', messages)


class OrderWorkflowTests(TestCase):
	def setUp(self):
		self.user = make_user('workflow', 'Sales Officer')
		self.product = make_product(stock=10)

	def stock(self):
		return Stock.objects.get(product=self.product).quantity_on_hand

	def test_confirming_issues_stock(self):
		order = make_order(product=self.product, quantity=3)

		advance_order_status(order, self.user)

		order.refresh_from_db()
		self.assertEqual(order.status, Order.Status.CONFIRMED)
		self.assertEqual(self.stock(), 7)

	def test_order_moves_pending_confirmed_on_the_way_delivered(self):
		order = make_order(product=self.product, quantity=2)
		self.assertEqual(order.status, Order.Status.PENDING)

		for expected in (Order.Status.CONFIRMED, Order.Status.ON_THE_WAY, Order.Status.DELIVERED):
			advance_order_status(order, self.user)
			order.refresh_from_db()
			self.assertEqual(order.status, expected)

		with self.assertRaises(OrderStatusError):
			advance_order_status(order, self.user)

	def test_advancing_order_updates_its_delivery(self):
		order = make_order(product=self.product, quantity=1)
		advance_order_status(order, self.user)
		delivery = Delivery.objects.create(order=order, address='Kumasi')

		advance_order_status(order, self.user)
		delivery.refresh_from_db()
		self.assertEqual(delivery.status, Delivery.Status.OUT_FOR_DELIVERY)

		advance_order_status(order, self.user)
		delivery.refresh_from_db()
		self.assertEqual(delivery.status, Delivery.Status.DELIVERED)
		self.assertIsNotNone(delivery.delivered_at)

	def test_delivery_status_drives_order_status(self):
		order = make_order(product=self.product, quantity=1)
		advance_order_status(order, self.user)
		delivery = Delivery.objects.create(order=order, address='Kumasi')

		for delivery_status, order_status in [
			(Delivery.Status.OUT_FOR_DELIVERY, Order.Status.ON_THE_WAY),
			(Delivery.Status.FAILED, Order.Status.CONFIRMED),
			(Delivery.Status.DELIVERED, Order.Status.DELIVERED),
		]:
			delivery.status = delivery_status
			delivery.save()
			sync_order_with_delivery(delivery)
			order.refresh_from_db()
			self.assertEqual(order.status, order_status)

	def test_order_on_the_way_cannot_be_cancelled(self):
		order = make_order(product=self.product, quantity=1)
		advance_order_status(order, self.user)
		advance_order_status(order, self.user)

		with self.assertRaises(OrderStatusError):
			cancel_order(order, self.user)

	def test_cancelling_confirmed_order_returns_stock(self):
		order = make_order(product=self.product, quantity=4)
		advance_order_status(order, self.user)

		cancel_order(order, self.user)

		order.refresh_from_db()
		self.assertEqual(order.status, Order.Status.CANCELLED)
		self.assertEqual(self.stock(), 10)

	def test_confirmed_order_with_payment_cannot_be_cancelled(self):
		order = make_order(product=self.product, quantity=2)
		advance_order_status(order, self.user)
		Payment.objects.create(order=order, amount='1.00', method=Payment.Method.CASH)

		with self.assertRaises(OrderStatusError):
			cancel_order(order, self.user)
		self.assertEqual(self.stock(), 8)
