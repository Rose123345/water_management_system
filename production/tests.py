from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from Inventory.models import Stock, StockMovement
from products.models import Product
from .models import ProductionBatch


class ProductionBatchTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(
			username='production-test-user',
			password='test-password',
		)
		self.product = Product.objects.create(
			name='Test Water',
			product_type=Product.ProductType.BOTTLED,
			package_size='500ml',
			unit_price='2.00',
		)
		self.client.force_login(self.user)

	def test_add_batch_records_product_and_user(self):
		response = self.client.post(reverse('production:add'), {
			'batch_number': 'BATCH-001',
			'product': self.product.pk,
			'production_date': '2026-09-28',
			'quantity_produced': 1200,
		})

		self.assertRedirects(response, reverse('production:list'))
		batch = ProductionBatch.objects.get(batch_number='BATCH-001')
		self.assertEqual(batch.product, self.product)
		self.assertEqual(batch.recorded_by, self.user)
		self.assertEqual(batch.quantity_produced, 1200)
		self.assertEqual(Stock.objects.get(product=self.product).quantity_on_hand, 1200)
		movement = StockMovement.objects.get(production_batch=batch)
		self.assertEqual(movement.movement_type, StockMovement.MovementType.PRODUCTION)
		self.assertEqual(movement.quantity, 1200)

	def test_history_displays_recorded_batch(self):
		ProductionBatch.objects.create(
			batch_number='BATCH-002',
			product=self.product,
			production_date='2026-09-27',
			quantity_produced=800,
			recorded_by=self.user,
		)

		response = self.client.get(reverse('production:list'))

		self.assertContains(response, 'BATCH-002')
		self.assertContains(response, 'Test Water')
		self.assertContains(response, '800')

	def test_zero_quantity_is_rejected(self):
		response = self.client.post(reverse('production:add'), {
			'batch_number': 'BATCH-003',
			'product': self.product.pk,
			'production_date': '2026-09-28',
			'quantity_produced': 0,
		})

		self.assertEqual(response.status_code, 200)
		self.assertFalse(ProductionBatch.objects.filter(batch_number='BATCH-003').exists())
		self.assertContains(response, 'Quantity produced must be greater than zero.')
