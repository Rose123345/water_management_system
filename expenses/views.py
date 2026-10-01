from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ExpenseCategoryForm, ExpenseForm
from .models import Expense, ExpenseCategory


@login_required
def expense_list(request):
	return render(request, 'expenses/expense_list.html', {
		'expenses': Expense.objects.select_related('category', 'recorded_by'),
		'categories': ExpenseCategory.objects.all(),
	})


@login_required
def expense_create(request):
	form = ExpenseForm(request.POST or None)
	if form.is_valid():
		expense = form.save(commit=False)
		expense.recorded_by = request.user
		expense.save()
		return redirect('expenses:list')
	return render(request, 'expenses/expense_form.html', {'form': form})


@login_required
def category_create(request):
	form = ExpenseCategoryForm(request.POST or None)
	if form.is_valid():
		form.save()
		return redirect('expenses:list')
	return render(request, 'expenses/category_form.html', {'form': form})
