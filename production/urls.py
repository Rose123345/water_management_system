from django.urls import path
from production import views

app_name = 'production'

urlpatterns = [
    path('', views.production_history, name='list'),
    path('add/', views.production_batch_add, name='add'),
]