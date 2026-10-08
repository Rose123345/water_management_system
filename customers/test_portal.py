from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.permissions import CUSTOMER_ROLE
from Inventory.services import low_stock_products
from products.models import Product
from sales.models import Order
from sales.testing import make_order, make_product, make_user

from .models import Customer


REGISTRATION = {
	'full_name': 'Ama Mensah', 'username': 'ama', 'phone': '024 123 4567',
	'email': 'ama@example.com', 'address': 'Kumasi',
	'password1': 'Safe-Test-Password-2026!', 'password2': 'Safe-Test-Password-2026!',
}


class CustomerRegistrationTests(TestCase):
	def test_register_creates_customer_account_and_opens_portal(self):
		response = self.client.post(reverse('accounts:register'), REGISTRATION, follow=True)

		self.assertRedirects(response, reverse('portal:home'))
		user = get_user_model().objects.get(username='ama')
		self.assertTrue(user.groups.filter(name=CUSTOMER_ROLE).exists())
		self.assertEqual(user.customer_profile.name, 'Ama Mensah')
		self.assertContains(response, 'Customer portal')
		self.assertContains(response, 'Customer account')
		self.assertNotContains(response, 'Access restricted')

	def test_register_rejects_invalid_phone(self):
		response = self.client.post(reverse('accounts:register'), {**REGISTRATION, 'phone': 'abc'})

		self.assertEqual(response.status_code, 200)
		self.assertFalse(get_user_model().objects.filter(username='ama').exists())

	def test_customer_login_lands_in_portal_and_staff_on_dashboard(self):
		self.client.post(reverse('accounts:register'), REGISTRATION)
		self.client.logout()
		make_user('seller', 'Sales Officer')

		customer_login = self.client.post(reverse('accounts:login'), {
			'username': 'ama', 'password': REGISTRATION['password1'],
		})
		self.assertRedirects(customer_login, reverse('portal:home'))

		self.client.logout()
		staff_login = self.client.post(reverse('accounts:login'), {
			'username': 'seller', 'password': 'safe-test-password',
		})
		self.assertRedirects(staff_login, reverse('dashboard:home'))


class CustomerPortalTests(TestCase):
	def setUp(self):
		self.user = make_user('ama', CUSTOMER_ROLE)
		self.customer = Customer.objects.create(name='Ama', phone='0241234567', user=self.user)
		self.product = make_product(price='6.50')
		self.client.force_login(self.user)

	def order_data(self, product, quantity):
		return {
			'items-TOTAL_FORMS': '3', 'items-INITIAL_FORMS': '0',
			'items-MIN_NUM_FORMS': '1', 'items-MAX_NUM_FORMS': '1000',
			'items-0-product': product.pk, 'items-0-quantity': quantity,
		}

	def test_customer_places_draft_order(self):
		response = self.client.post(reverse('portal:order_add'), self.order_data(self.product, 3))

		order = Order.objects.get(customer=self.customer)
		self.assertRedirects(response, reverse('portal:order_detail', args=[order.pk]))
		self.assertEqual(order.status, Order.Status.DRAFT)
		self.assertEqual(order.created_by, self.user)
		self.assertEqual(order.total, Decimal('19.50'))

	def test_empty_order_is_rejected(self):
		data = self.order_data(self.product, 1)
		data.pop('items-0-product')
		data.pop('items-0-quantity')

		response = self.client.post(reverse('portal:order_add'), data)

		self.assertEqual(response.status_code, 200)
		self.assertFalse(Order.objects.exists())

	def test_inactive_product_cannot_be_ordered(self):
		retired = make_product(name='Retired', status=Product.Status.INACTIVE)

		self.client.post(reverse('portal:order_add'), self.order_data(retired, 1))

		self.assertFalse(Order.objects.exists())

	def test_inactive_customer_cannot_order(self):
		Customer.objects.filter(pk=self.customer.pk).update(status=Customer.Status.INACTIVE)

		response = self.client.get(reverse('portal:order_add'))

		self.assertRedirects(response, reverse('portal:home'))

	def test_customer_only_sees_own_orders(self):
		own = make_order(customer=self.customer, product=self.product)
		other = make_order(product=self.product)

		home = self.client.get(reverse('portal:home'))
		self.assertContains(home, own.order_number)
		self.assertNotContains(home, other.order_number)
		self.assertEqual(self.client.get(reverse('portal:order_detail', args=[other.pk])).status_code, 404)
		self.client.post(reverse('portal:order_cancel', args=[other.pk]))
		other.refresh_from_db()
		self.assertEqual(other.status, Order.Status.DRAFT)

	def test_customer_can_cancel_draft_but_not_confirmed_order(self):
		draft = make_order(customer=self.customer, product=self.product)
		confirmed = make_order(customer=self.customer, product=self.product, status=Order.Status.CONFIRMED)

		self.client.post(reverse('portal:order_cancel', args=[draft.pk]))
		self.client.post(reverse('portal:order_cancel', args=[confirmed.pk]))

		draft.refresh_from_db()
		confirmed.refresh_from_db()
		self.assertEqual(draft.status, Order.Status.CANCELLED)
		self.assertEqual(confirmed.status, Order.Status.CONFIRMED)

	def test_products_page_shows_availability_of_active_products(self):
		make_product(name='Full Stock', stock=500)
		make_product(name='Retired', status=Product.Status.INACTIVE)

		response = self.client.get(reverse('portal:products'))

		self.assertContains(response, 'Full Stock')
		self.assertContains(response, 'In stock')
		self.assertContains(response, 'Out of stock')  # self.product has never been stocked
		self.assertNotContains(response, 'Retired')
		self.assertContains(response, 'href="/my-account/products/"')

	def test_order_link_preselects_product(self):
		response = self.client.get(reverse('portal:order_add'), {'product': self.product.pk})

		self.assertContains(response, f'<option value="{self.product.pk}" selected>', html=False)

	def test_customer_sees_friendly_page_on_staff_areas(self):
		response = self.client.get(reverse('dashboard:home'))

		self.assertEqual(response.status_code, 403)
		self.assertContains(response, 'This area is for staff', status_code=403)
		self.assertContains(response, reverse('portal:home'), status_code=403)

	def test_staff_cannot_use_portal(self):
		self.client.force_login(make_user('seller', 'Sales Officer'))

		self.assertEqual(self.client.get(reverse('portal:home')).status_code, 403)


class CustomerWithoutProfileTests(TestCase):
	def test_customer_without_record_completes_details_first(self):
		user = make_user('walkin', CUSTOMER_ROLE)
		self.client.force_login(user)

		self.assertRedirects(self.client.get(reverse('portal:home')), reverse('portal:profile'))

		response = self.client.post(reverse('portal:profile'), {
			'name': 'Walk In', 'phone': '0240000009', 'email': '', 'address': 'Accra',
		})

		self.assertRedirects(response, reverse('portal:home'))
		self.assertEqual(Customer.objects.get(user=user).name, 'Walk In')


class ActivationTests(TestCase):
	def test_activation_requires_post(self):
		self.client.force_login(make_user('desk', 'Customer Service Officer'))
		customer = Customer.objects.create(name='Dormant', phone='0240000000', status=Customer.Status.INACTIVE)
		url = reverse('customers:activate', args=[customer.pk])

		self.assertEqual(self.client.get(url).status_code, 405)
		self.client.post(url)
		customer.refresh_from_db()
		self.assertEqual(customer.status, Customer.Status.ACTIVE)


class LowStockTests(TestCase):
	def test_low_stock_includes_never_stocked_active_products_only(self):
		never_stocked = make_product(name='New line')
		make_product(name='Plenty', stock=500)
		make_product(name='Retired', status=Product.Status.INACTIVE)

		self.assertEqual(list(low_stock_products()), [never_stocked])
