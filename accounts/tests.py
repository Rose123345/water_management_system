from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse


class LoginPageTests(TestCase):
	def test_login_page_is_available_to_authenticated_users(self):
		from django.contrib.auth import get_user_model

		user = get_user_model().objects.create_user(username='operator', password='safe-test-password')
		self.client.force_login(user)

		response = self.client.get('/accounts/')

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'name="username"')
		self.assertContains(response, 'name="password"')

	def test_public_header_always_shows_login_link(self):
		response = self.client.get('/')

		self.assertContains(response, 'href="/accounts/">Log in</a>')

	def test_registration_page_uses_existing_template(self):
		response = self.client.get('/accounts/register/')

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Create account')


class UserRoleAdminTests(TestCase):
	def setUp(self):
		self.admin_user = get_user_model().objects.create_superuser(
			username='admin-test', password='safe-test-password', email='admin@example.com'
		)
		self.role = Group.objects.create(name='Inventory Officer')
		self.client.force_login(self.admin_user)

	def test_add_user_form_includes_role_selector(self):
		response = self.client.get(reverse('admin:auth_user_add'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'name="groups"')
		self.assertContains(response, 'Roles')
		self.assertContains(response, 'Inventory Officer')

	def test_user_can_be_created_with_role_selected(self):
		response = self.client.post(reverse('admin:auth_user_add'), {
			'username': 'new-inventory-user',
			'password1': 'Safe-Test-Password-2026!',
			'password2': 'Safe-Test-Password-2026!',
			'groups': [self.role.pk],
		})

		self.assertEqual(response.status_code, 302)
		user = get_user_model().objects.get(username='new-inventory-user')
		self.assertIn(self.role, user.groups.all())
