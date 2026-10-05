from django.shortcuts import redirect, render
from accounts.permissions import ROLE_ACCESS, role_required

from .forms import ExpenseCategoryForm, ExpenseForm
from .models import Expense, ExpenseCategory


@role_required(*ROLE_ACCESS['expenses'])
def expense_list(request):
	return render(request, 'expenses/expense_list.html', {
		'expenses': Expense.objects.select_related('category', 'recorded_by'),
		'categories': ExpenseCategory.objects.all(),
	})


@role_required(*ROLE_ACCESS['expenses'])
def expense_create(request):
	form = ExpenseForm(request.POST or None)
	if form.is_valid():
		expense = form.save(commit=False)
		expense.recorded_by = request.user
		expense.save()
		return redirect('expenses:list')
	return render(request, 'expenses/expense_form.html', {'form': form})


@role_required(*ROLE_ACCESS['expenses'])
def category_create(request):
	form = ExpenseCategoryForm(request.POST or None)
	if form.is_valid():
		form.save()
		return redirect('expenses:list')
	return render(request, 'expenses/category_form.html', {'form': form})
