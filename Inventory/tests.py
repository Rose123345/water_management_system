from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from products.models import Product
from .models import Stock, StockMovement


class InventoryTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(
			username='inventory-test-user',
			password='test-password',
		)
		self.client.force_login(self.user)
		self.product = Product.objects.create(
			name='Test Water',
			product_type=Product.ProductType.BOTTLED,
			package_size='500ml',
			unit_price='2.00',
			reorder_level=100,
		)

	def test_receipt_and_issue_update_stock(self):
		receipt_response = self.client.post(reverse('inventory:movement_add'), {
			'product': self.product.pk,
			'movement_type': StockMovement.MovementType.RECEIPT,
			'quantity': 200,
			'note': 'Supplier delivery',
		})
		self.assertRedirects(receipt_response, reverse('inventory:list'))

		issue_response = self.client.post(reverse('inventory:movement_add'), {
			'product': self.product.pk,
			'movement_type': StockMovement.MovementType.ISSUE,
			'quantity': 75,
			'note': 'Dispatch',
		})
		self.assertRedirects(issue_response, reverse('inventory:list'))
		self.assertEqual(Stock.objects.get(product=self.product).quantity_on_hand, 125)
		self.assertEqual(StockMovement.objects.count(), 2)

	def test_issue_cannot_make_stock_negative(self):
		response = self.client.post(reverse('inventory:movement_add'), {
			'product': self.product.pk,
			'movement_type': StockMovement.MovementType.ISSUE,
			'quantity': 1,
			'note': 'Over-issue',
		})

		self.assertEqual(response.status_code, 200)
		self.assertFalse(StockMovement.objects.exists())
		self.assertContains(response, 'Cannot issue more stock than is currently available.')

	def test_manual_form_rejects_production_movement_type(self):
		response = self.client.post(reverse('inventory:movement_add'), {
			'product': self.product.pk,
			'movement_type': StockMovement.MovementType.PRODUCTION,
			'quantity': 10,
		})

		self.assertEqual(response.status_code, 200)
		self.assertFalse(StockMovement.objects.exists())

	def test_dashboard_flags_products_below_reorder_level(self):
		Stock.objects.create(product=self.product, quantity_on_hand=99)

		response = self.client.get(reverse('inventory:list'))

		self.assertContains(response, 'Low Stock')
		self.assertContains(response, 'Test Water')
		self.assertEqual(list(response.context['low_stock_products']), [self.product])

# Create your tests here.
