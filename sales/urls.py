from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.order_list, name='list'),
    path('add/', views.order_add, name='add'),
    path('<int:pk>/', views.order_detail, name='detail'),
    path('<int:pk>/advance/', views.order_advance, name='advance'),
    path('<int:pk>/cancel/', views.order_cancel, name='cancel'),
]