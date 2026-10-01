from django.test import TestCase


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
