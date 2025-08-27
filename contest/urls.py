# In contest/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # This URL will show the form to request sub-admin permissions
    path('request-sub-admin/', views.request_sub_admin, name='request_sub_admin'),

    # This URL will be shown after a successful request
    path('request-success/', views.request_sub_admin_success, name='request_sub_admin_success'),
    
    path('create/', views.create_contest, name='create_contest'),
    
    path('my-contests/', views.manage_my_contests, name='manage_my_contests'),
    path('<int:contest_id>/manage/', views.manage_contest_detail, name='manage_contest_detail'),
    
    path('', views.contest_list, name='contest_list'),
    
    path('<int:contest_id>/', views.contest_detail, name='contest_detail'),

    path('<int:contest_id>/register/', views.register_for_contest, name='register_for_contest'),
    
    path('<int:contest_id>/compete/', views.contest_interface, name='contest_interface'),

    path('<int:contest_id>/problem/<int:problem_id>/submit/', views.submit_contest_problem, name='submit_contest_problem'),

    path('<int:contest_id>/my-submissions/', views.my_contest_submissions, name='my_contest_submissions'),
]