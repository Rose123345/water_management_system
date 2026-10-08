from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.shortcuts import redirect, render
from accounts.permissions import ROLE_ACCESS, role_required
from .forms import StockMovementForm
from .models import StockMovement
from .services import low_stock_products, products_with_stock, record_stock_movement


@role_required(*ROLE_ACCESS['inventory'])
def stock_dashboard(request):
	products = products_with_stock().order_by('name')
	low_stock = low_stock_products()
	movements = StockMovement.objects.select_related(
		'product', 'recorded_by', 'production_batch'
	)[:100]
	return render(request, 'Inventory/stock_dashboard.html', {
		'products': products,
		'low_stock_products': low_stock,
		'product_count': products.count(),
		'units_on_hand': products.aggregate(total=Sum('stock_quantity'))['total'] or 0,
		'low_stock_count': low_stock.count(),
		'movements': movements,
	})


@role_required(*ROLE_ACCESS['inventory'])
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
