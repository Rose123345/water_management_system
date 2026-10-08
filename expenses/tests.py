from django.test import TestCase
from django.urls import reverse

from sales.testing import make_user

from .models import Expense, ExpenseCategory


class ExpensePageTests(TestCase):
	def setUp(self):
		self.category = ExpenseCategory.objects.create(name='Fuel')

	def test_accountant_can_record_expense(self):
		self.client.force_login(make_user('books', 'Accountant'))

		response = self.client.post(reverse('expenses:add'), {
			'category': self.category.pk, 'description': 'Truck diesel',
			'amount': '120.00', 'expense_date': '2026-10-01',
		})

		self.assertRedirects(response, reverse('expenses:list'))
		self.assertEqual(Expense.objects.get().description, 'Truck diesel')

	def test_rejects_non_positive_amount(self):
		self.client.force_login(make_user('books', 'Accountant'))

		response = self.client.post(reverse('expenses:add'), {
			'category': self.category.pk, 'description': 'Bad',
			'amount': '0', 'expense_date': '2026-10-01',
		})

		self.assertEqual(response.status_code, 200)
		self.assertFalse(Expense.objects.exists())

	def test_other_roles_are_denied(self):
		self.client.force_login(make_user('seller', 'Sales Officer'))

		self.assertEqual(self.client.get(reverse('expenses:list')).status_code, 403)
