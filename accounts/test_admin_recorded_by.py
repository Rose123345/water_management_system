from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from expenses.models import Expense, ExpenseCategory
from Inventory.models import Stock
from production.models import ProductionBatch
from products.models import Product
from sales.testing import make_order, make_product


class AdminRecordsSignedInUserTests(TestCase):
	def setUp(self):
		self.admin_user = get_user_model().objects.create_superuser(
			username='boss', password='safe-test-password', email='boss@example.com'
		)
		get_user_model().objects.create_user(username='someone-else', password='safe-test-password')
		self.client.force_login(self.admin_user)

	def test_add_pages_do_not_offer_a_user_dropdown(self):
		for url_name, field in [
			('admin:products_product_add', 'created_by'),
			('admin:customers_customer_add', 'created_by'),
			('admin:production_productionbatch_add', 'recorded_by'),
			('admin:expenses_expense_add', 'recorded_by'),
			('admin:payment_payment_add', 'received_by'),
		]:
			with self.subTest(url_name):
				response = self.client.get(reverse(url_name))
				self.assertEqual(response.status_code, 200)
				self.assertNotContains(response, f'name="{field}"')

	def test_new_product_is_created_by_signed_in_admin(self):
		response = self.client.post(reverse('admin:products_product_add'), {
			'name': 'Admin Bottle', 'product_type': Product.ProductType.BOTTLED,
			'package_size': '1.5L', 'unit_price': '9.00', 'reorder_level': '50',
			'status': Product.Status.ACTIVE, 'description': '',
		})

		self.assertEqual(response.status_code, 302)
		self.assertEqual(Product.objects.get(name='Admin Bottle').created_by, self.admin_user)

	def test_new_expense_is_recorded_by_signed_in_admin(self):
		category = ExpenseCategory.objects.create(name='Utilities')

		self.client.post(reverse('admin:expenses_expense_add'), {
			'category': category.pk, 'description': 'Power', 'amount': '50.00', 'expense_date': '2026-10-08',
		})

		self.assertEqual(Expense.objects.get().recorded_by, self.admin_user)

	def test_new_payment_is_received_by_signed_in_admin(self):
		order = make_order()

		self.client.post(reverse('admin:payment_payment_add'), {
			'order': order.pk, 'amount': '2.00', 'method': 'cash', 'status': 'completed', 'reference': '',
		})

		self.assertEqual(order.payments.get().received_by, self.admin_user)

	def test_production_batch_added_in_admin_adds_stock(self):
		product = make_product()

		self.client.post(reverse('admin:production_productionbatch_add'), {
			'batch_number': 'B-100', 'product': product.pk,
			'production_date': '2026-10-08', 'quantity_produced': '240',
		})

		batch = ProductionBatch.objects.get(batch_number='B-100')
		self.assertEqual(batch.recorded_by, self.admin_user)
		self.assertEqual(Stock.objects.get(product=product).quantity_on_hand, 240)
		self.assertEqual(batch.stock_movement.quantity, 240)
