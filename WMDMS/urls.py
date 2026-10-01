"""
URL configuration for WMDMS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('contact/', include('contact.urls')),
    path('admin/', admin.site.urls),
    path('customers/products', lambda request: redirect('products:list')),
    path('customers/products/', lambda request: redirect('products:list')),
    path('customers/', include('customers.urls')),  # Include the URLs from the customers app
    path('accounts/', include('accounts.urls')),  # Include the URLs from the accounts app
    path('products/', include('products.urls')),  # Include the URLs from the products app
    path('production/', include('production.urls')),  # Include the URLs from the production app
    path('Inventory/', include('Inventory.urls')),  # Include the URLs from the Inventory app
    path('payments/', include('payment.urls')),  # Include the URLs from the payments app
    path('expenses/', include('expenses.urls')),  # Include the URLs from the expenses app
    path('sales/', include('sales.urls')),  # Include the URLs from the sales app
    path('distribution/', include('distribution.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('reports/', include('reports.urls')),
]


