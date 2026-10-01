from django.test import TestCase

from django.contrib.auth import get_user_model


class CustomerPageTests(TestCase):
	def test_customer_list_is_available_to_signed_in_users(self):
		user = get_user_model().objects.create_user(username='customer-operator', password='safe-test-password')
		self.client.force_login(user)

		response = self.client.get('/customers/')

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Customers')
		self.assertContains(response, 'Customers</a>')

	def test_customer_list_requires_login(self):
		response = self.client.get('/customers/')

		self.assertRedirects(response, '/accounts/?next=/customers/')
