from django.urls import path

from . import portal_views

app_name = 'portal'

urlpatterns = [
    path('', portal_views.portal_home, name='home'),
    path('products/', portal_views.portal_products, name='products'),
    path('profile/', portal_views.portal_profile, name='profile'),
    path('orders/new/', portal_views.portal_order_create, name='order_add'),
    path('orders/<int:pk>/', portal_views.portal_order_detail, name='order_detail'),
    path('orders/<int:pk>/cancel/', portal_views.portal_order_cancel, name='order_cancel'),
]
