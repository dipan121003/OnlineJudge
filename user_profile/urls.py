# In user_profile/urls.py
from django.urls import path
from .views import profile_view

urlpatterns = [
    # This will create a URL like /profile/some_username/
    path('<str:username>/', profile_view, name='profile_view'),
]