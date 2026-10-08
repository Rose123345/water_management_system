
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from accounts.permissions import ROLE_ACCESS, role_required
from .models import Customer
from .forms import CustomerForm


@role_required(*ROLE_ACCESS['customers'])
def customer_list(request):
    query = request.GET.get('q', '')
    customers = Customer.objects.all()
    if query:
        customers = customers.filter(name__icontains=query)
    return render(request, 'list.html', {
        'customers': customers, 'query': query
    })


@role_required(*ROLE_ACCESS['customers'])
def customer_add(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.created_by = request.user
            customer.save()
            messages.success(request, f"Customer '{customer.name}' was added.")
            return redirect('customers:list')
    else:
        form = CustomerForm()
    return render(request, 'customer_form.html', {'form': form, 'title': 'Add Customer'})


@role_required(*ROLE_ACCESS['customers'])
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, f"Customer '{customer.name}' was updated.")
            return redirect('customers:list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'customer_form.html', {'form': form, 'title': 'Edit Customer'})


@role_required(*ROLE_ACCESS['customers'])
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, 'customer_detail.html', {'customer': customer})


@role_required(*ROLE_ACCESS['customers'])
def customer_deactivate(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.status = Customer.Status.INACTIVE
        customer.save()
        messages.success(request, f"Customer '{customer.name}' was deactivated.")
        return redirect('customers:list')
    return render(request, 'customer_confirm_deactivate.html', {'customer': customer})


@role_required(*ROLE_ACCESS['customers'])
@require_POST
def customer_activate(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.status = Customer.Status.ACTIVE
    customer.save()
    messages.success(request, f"Customer '{customer.name}' was reactivated.")
    return redirect('customers:list')