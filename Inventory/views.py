from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import F, Q, Value
from django.db.models.functions import Coalesce
from django.shortcuts import redirect, render
from products.models import Product
from .forms import StockMovementForm
from .models import StockMovement
from .services import record_stock_movement


@login_required
def stock_dashboard(request):
	products = Product.objects.annotate(
		stock_quantity=Coalesce('stock__quantity_on_hand', Value(0)),
	).order_by('name')
	low_stock_products = products.filter(
		Q(stock__isnull=True) | Q(stock__quantity_on_hand__lte=F('reorder_level'))
	)
	movements = StockMovement.objects.select_related(
		'product', 'recorded_by', 'production_batch'
	)[:100]
	return render(request, 'Inventory/stock_dashboard.html', {
		'products': products,
		'low_stock_products': low_stock_products,
		'movements': movements,
	})


@login_required
def stock_movement_add(request):
	if request.method == 'POST':
		form = StockMovementForm(request.POST)
		if form.is_valid():
			movement = form.save(commit=False)
			try:
				record_stock_movement(
					product=movement.product,
					movement_type=movement.movement_type,
					quantity=movement.quantity,
					recorded_by=request.user,
					note=movement.note,
				)
			except ValidationError as error:
				form.add_error(None, error)
			else:
				messages.success(request, 'Stock movement recorded.')
				return redirect('inventory:list')
	else:
		form = StockMovementForm()

	return render(request, 'Inventory/stock_movement_form.html', {'form': form})
