from django.urls import path
from expenses import views

app_name = 'expenses'

urlpatterns = [
	path('', views.expense_list, name='list'),
	path('add/', views.expense_create, name='add'),
	path('categories/add/', views.category_create, name='category_add'),
]