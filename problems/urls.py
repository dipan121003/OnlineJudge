from django.urls import path
from .views import problems_list, problem_detail

urlpatterns = [
    path('list/', problems_list, name='problems-list'),  # URL for the problems list view
    path('detail/<int:problem_id>/', problem_detail, name='problem-detail'),  # URL for the problem detail view
]