from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from customers.models import Customer
from products.models import Product
from .models import Order, OrderItem


class OrderAdminTests(TestCase):
	def setUp(self):
		self.admin_user = get_user_model().objects.create_superuser(
			username='sales-admin', password='safe-test-password', email='sales@example.com'
		)
		self.customer = Customer.objects.create(name='Admin Customer', phone='0240000000')
		self.product = Product.objects.create(
			name='Admin Product',
			product_type=Product.ProductType.BOTTLED,
			package_size='500ml',
			unit_price='3.50',
		)
		self.client.force_login(self.admin_user)

	def test_order_admin_add_shows_products_but_keeps_status_calculated(self):
		response = self.client.get(reverse('admin:sales_order_add'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'name="items-0-product"')
		self.assertContains(response, 'Admin Product (500ml)')
		self.assertContains(response, 'Pending')
		self.assertContains(response, 'Calculated from order items after saving')
		self.assertNotContains(response, 'name="status"')
		self.assertNotContains(response, 'name="total"')

	def test_admin_can_create_draft_order_with_product_items(self):
		response = self.client.post(reverse('admin:sales_order_add'), {
			'customer': self.customer.pk,
			'items-TOTAL_FORMS': '1',
			'items-INITIAL_FORMS': '0',
			'items-MIN_NUM_FORMS': '0',
			'items-MAX_NUM_FORMS': '1000',
			'items-0-product': self.product.pk,
			'items-0-quantity': '3',
			'items-0-unit_price': '',
		})

		self.assertEqual(response.status_code, 302)
		order = Order.objects.get(customer=self.customer)
		item = OrderItem.objects.get(order=order)
		self.assertEqual(order.status, Order.Status.PENDING)
		self.assertEqual(item.quantity, 3)
		self.assertEqual(item.unit_price, Decimal('3.50'))
