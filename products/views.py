from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product
from .forms import ProductForm


def in_groups(user, group_names):
    return user.groups.filter(name__in=group_names).exists() or user.is_superuser


def public_product_list(request):
    products = Product.objects.filter(status=Product.Status.ACTIVE)
    query = request.GET.get('q', '').strip()
    product_type = request.GET.get('type', '')

    if query:
        products = products.filter(name__icontains=query)
    if product_type in Product.ProductType.values:
        products = products.filter(product_type=product_type)

    return render(request, 'products/public_product_list.html', {
        'products': products,
        'query': query,
        'selected_type': product_type,
        'product_types': Product.ProductType.choices,
    })


@login_required
def product_list(request):
    query = request.GET.get('q', '')
    products = Product.objects.all()
    if query:
        products = products.filter(name__icontains=query)
    return render(request, 'products/product_list.html', {
        'products': products, 'query': query,
        'can_manage': in_groups(request.user, ['Administrator']),
    })


@login_required
def product_add(request):
    if not in_groups(request.user, ['Administrator']):
        messages.error(request, "You don't have permission to add products.")
        return redirect('products:list')

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
            messages.success(request, f"Product '{product.name}' was added.")
            return redirect('products:list')
    else:
        form = ProductForm()
    return render(request, 'products/product_form.html', {'form': form, 'title': 'Add Product'})


@login_required
def product_edit(request, pk):
    if not in_groups(request.user, ['Administrator']):
        messages.error(request, "You don't have permission to edit products.")
        return redirect('products:list')

    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Product '{product.name}' was updated.")
            return redirect('products:list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/product_form.html', {'form': form, 'title': 'Edit Product'})


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/product_detail.html', {'product': product})


@login_required
def product_deactivate(request, pk):
    if not in_groups(request.user, ['Administrator']):
        messages.error(request, "You don't have permission to deactivate products.")
        return redirect('products:list')

    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.status = Product.Status.INACTIVE
        product.save()
        messages.success(request, f"Product '{product.name}' was deactivated.")
        return redirect('products:list')
    return render(request, 'products/product_confirm_deactivate.html', {'product': product})


@login_required
def product_activate(request, pk):
    if not in_groups(request.user, ['Administrator']):
        messages.error(request, "You don't have permission to activate products.")
        return redirect('products:list')

    product = get_object_or_404(Product, pk=pk)
    product.status = Product.Status.ACTIVE
    product.save()
    messages.success(request, f"Product '{product.name}' was reactivated.")
    return redirect('products:list')