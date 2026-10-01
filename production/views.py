from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from Inventory.models import StockMovement
from Inventory.services import record_stock_movement
from django.shortcuts import redirect, render
from .forms import ProductionBatchForm
from .models import ProductionBatch


@login_required
def production_history(request):
	batches = ProductionBatch.objects.select_related('product', 'recorded_by')
	return render(request, 'production/production_history.html', {'batches': batches})


@login_required
def production_batch_add(request):
	if request.method == 'POST':
		form = ProductionBatchForm(request.POST)
		if form.is_valid():
			with transaction.atomic():
				batch = form.save(commit=False)
				batch.recorded_by = request.user
				batch.save()
				record_stock_movement(
					product=batch.product,
					movement_type=StockMovement.MovementType.PRODUCTION,
					quantity=batch.quantity_produced,
					recorded_by=request.user,
					note=f'Produced from batch {batch.batch_number}',
					production_batch=batch,
				)
			messages.success(request, f'Production batch {batch.batch_number} was recorded.')
			return redirect('production:list')
	else:
		form = ProductionBatchForm()

	return render(request, 'production/production_batch_form.html', {'form': form})
