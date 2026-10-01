from django.urls import path
from Inventory import views

app_name = 'inventory'

urlpatterns = [
	path('', views.stock_dashboard, name='list'),
	path('movements/add/', views.stock_movement_add, name='movement_add'),
]