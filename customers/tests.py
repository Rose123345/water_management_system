from django.test import TestCase

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


class CustomerPageTests(TestCase):
	def test_customer_list_is_available_to_customer_service_role(self):
		user = get_user_model().objects.create_user(username='customer-operator', password='safe-test-password')
		user.groups.add(Group.objects.create(name='Customer Service Officer'))
		self.client.force_login(user)

		response = self.client.get('/customers/')

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Customers')
		self.assertContains(response, 'href="/customers/"')
		self.assertContains(response, '<use href="#nav-customers"></use>', html=False)

	def test_customer_list_denies_signed_in_user_without_role(self):
		user = get_user_model().objects.create_user(username='unassigned', password='safe-test-password')
		self.client.force_login(user)

		response = self.client.get('/customers/')

		self.assertEqual(response.status_code, 403)

	def test_customer_list_requires_login(self):
		response = self.client.get('/customers/')

		self.assertRedirects(response, '/accounts/?next=/customers/')
