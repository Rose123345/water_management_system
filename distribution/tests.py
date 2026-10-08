from django.test import TestCase
from django.urls import reverse

from sales.models import Order
from sales.testing import make_order, make_user

from .forms import DeliveryForm
from .models import Delivery


class DeliveryFormTests(TestCase):
	def setUp(self):
		self.driver = make_user('driver', 'Distribution Officer')
		make_user('seller', 'Sales Officer')
		self.confirmed = make_order(status=Order.Status.CONFIRMED)
		make_order(customer=self.confirmed.customer, product=self.confirmed.items.get().product)

	def test_only_confirmed_orders_and_distribution_staff_are_offered(self):
		form = DeliveryForm()

		self.assertEqual(list(form.fields['order'].queryset), [self.confirmed])
		self.assertEqual(list(form.fields['assigned_to'].queryset), [self.driver])

	def test_order_with_a_delivery_is_no_longer_offered(self):
		Delivery.objects.create(order=self.confirmed, address='12 Ring Road')

		self.assertFalse(DeliveryForm().fields['order'].queryset.exists())

	def test_delivered_at_follows_status(self):
		self.client.force_login(self.driver)
		data = {
			'order': self.confirmed.pk, 'address': '12 Ring Road', 'assigned_to': self.driver.pk,
			'status': Delivery.Status.DELIVERED, 'scheduled_date': '2026-10-08',
		}

		self.client.post(reverse('distribution:add'), data)
		delivery = Delivery.objects.get()
		self.assertIsNotNone(delivery.delivered_at)

		self.client.post(reverse('distribution:edit', args=[delivery.pk]), {**data, 'status': Delivery.Status.FAILED})
		delivery.refresh_from_db()
		self.assertIsNone(delivery.delivered_at)

	def test_saving_delivery_moves_order_on_the_way(self):
		self.client.force_login(self.driver)

		self.client.post(reverse('distribution:add'), {
			'order': self.confirmed.pk, 'address': '12 Ring Road', 'assigned_to': self.driver.pk,
			'status': Delivery.Status.OUT_FOR_DELIVERY, 'scheduled_date': '2026-10-08',
		})

		self.confirmed.refresh_from_db()
		self.assertEqual(self.confirmed.status, Order.Status.ON_THE_WAY)
