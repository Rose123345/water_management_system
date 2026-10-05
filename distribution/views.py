from django.shortcuts import get_object_or_404, redirect, render
from accounts.permissions import ROLE_ACCESS, role_required

from .forms import DeliveryForm
from .models import Delivery


@role_required(*ROLE_ACCESS['distribution'])
def delivery_list(request):
	deliveries = Delivery.objects.select_related('order__customer', 'assigned_to')
	status = request.GET.get('status')
	if status:
		deliveries = deliveries.filter(status=status)
	return render(request, 'distribution/delivery_list.html', {
		'deliveries': deliveries, 'statuses': Delivery.Status.choices, 'selected_status': status,
	})


@role_required(*ROLE_ACCESS['distribution'])
def delivery_create(request):
	form = DeliveryForm(request.POST or None)
	if form.is_valid():
		form.save()
		return redirect('distribution:list')
	return render(request, 'distribution/delivery_form.html', {'form': form})


@role_required(*ROLE_ACCESS['distribution'])
def delivery_edit(request, pk):
	delivery = get_object_or_404(Delivery, pk=pk)
	form = DeliveryForm(request.POST or None, instance=delivery)
	if form.is_valid():
		form.save()
		return redirect('distribution:list')
	return render(request, 'distribution/delivery_form.html', {'form': form, 'delivery': delivery})
