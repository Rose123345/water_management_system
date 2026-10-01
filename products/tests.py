from django.test import TestCase

from .models import Product


class PublicProductListTests(TestCase):
	def setUp(self):
		Product.objects.create(
			name='Spring Bottle',
			product_type=Product.ProductType.BOTTLED,
			package_size='750ml',
			unit_price='12.50',
			status=Product.Status.ACTIVE,
		)
		Product.objects.create(
			name='Old Bottle',
			product_type=Product.ProductType.BOTTLED,
			package_size='500ml',
			unit_price='8.00',
			status=Product.Status.INACTIVE,
		)

	def test_public_catalogue_shows_only_active_products(self):
		response = self.client.get('/products/')

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Spring Bottle')
		self.assertNotContains(response, 'Old Bottle')

	def test_public_catalogue_filters_by_name_and_type(self):
		response = self.client.get('/products/', {'q': 'Spring', 'type': 'bottled'})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Spring Bottle')
		self.assertNotContains(response, 'Old Bottle')
