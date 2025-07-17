from django.urls import path
from .views import problems_list

urlpatterns = [
    path('list/', problems_list, name='problems-list'),  # URL for the problems list view
]