from django.urls import path, include
from .views import register_user,login_user

urlpatterns = [
    path('register/', register_user, name='register-user'),
    path('login/', login_user, name='login-user'),
]