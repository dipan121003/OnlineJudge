# In user_profile/urls.py
from django.urls import path
from .views import profile_view, edit_profile, leaderboard_view

urlpatterns = [
    path('leaderboard/', leaderboard_view, name='leaderboard'),
    # This will create a URL like /profile/some_username/
    path('<str:username>/', profile_view, name='profile_view'),
    
    path('<str:username>/edit/', edit_profile, name='edit_profile'),
]