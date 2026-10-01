from django.urls import path
from products import views

app_name = 'products'

urlpatterns = [
    path('', views.public_product_list, name='catalogue'),
    path('manage/', views.product_list, name='list'),
    path('add/', views.product_add, name='add'),
    path('<int:pk>/', views.product_detail, name='detail'),
    path('<int:pk>/edit/', views.product_edit, name='edit'),
    path('<int:pk>/deactivate/', views.product_deactivate, name='deactivate'),
    path('<int:pk>/activate/', views.product_activate, name='activate'),
]