from django.urls import path
from . import views


app_name = 'customers'

urlpatterns = [
    path('', views.customer_list, name='list'),
    path('add/', views.customer_add, name='add'),
    path('<int:pk>/', views.customer_detail, name='detail'),
    path('<int:pk>/edit/', views.customer_edit, name='edit'),
    path('<int:pk>/deactivate/', views.customer_deactivate, name='deactivate'),
    path('<int:pk>/activate/', views.customer_activate, name='activate'),
]