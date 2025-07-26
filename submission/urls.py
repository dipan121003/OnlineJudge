# submission/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('run/', views.submit_code, name='run_code'),
]