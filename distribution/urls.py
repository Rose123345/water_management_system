from django.urls import path
from distribution import views

app_name = 'distribution'

urlpatterns = [
	path('', views.delivery_list, name='list'),
	path('add/', views.delivery_create, name='add'),
	path('<int:pk>/edit/', views.delivery_edit, name='edit'),
]