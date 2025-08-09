# In contest/urls.py
from django.urls import path
from .views import request_sub_admin, request_sub_admin_success, create_contest, contest_list, contest_detail, register_for_contest, contest_interface, submit_contest_problem

urlpatterns = [
    # This URL will show the form to request sub-admin permissions
    path('request-sub-admin/', request_sub_admin, name='request_sub_admin'),

    # This URL will be shown after a successful request
    path('request-success/', request_sub_admin_success, name='request_sub_admin_success'),
    
    path('create/', create_contest, name='create_contest'),
    
    path('', contest_list, name='contest_list'),
    
    path('<int:contest_id>/', contest_detail, name='contest_detail'),

    path('<int:contest_id>/register/', register_for_contest, name='register_for_contest'),
    
    path('<int:contest_id>/compete/', contest_interface, name='contest_interface'),

    path('<int:contest_id>/problem/<int:problem_id>/submit/', submit_contest_problem, name='submit_contest_problem'),

]