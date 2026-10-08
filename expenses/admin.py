from django.contrib import admin

from accounts.admin_mixins import RecordedByAdminMixin

from .models import Expense, ExpenseCategory


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)


@admin.register(Expense)
class ExpenseAdmin(RecordedByAdminMixin, admin.ModelAdmin):
	recorded_by_field = 'recorded_by'
	list_display = ('description', 'category', 'amount', 'expense_date', 'recorded_by')
	list_filter = ('category', 'expense_date')
	search_fields = ('description',)
