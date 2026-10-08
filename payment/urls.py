from django.urls import path

from . import views

app_name = 'payments'

urlpatterns = [
	path('order/<int:order_pk>/', views.payment_list, name='list'),
	path('order/<int:order_pk>/add/', views.payment_create, name='add'),
	path('paystack/webhook/', views.paystack_webhook, name='paystack_webhook'),
]
