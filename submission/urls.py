# submission/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('run/', views.submit_code, name='run_code'),
    
    # URL for handling the "Submit Solution" button
    path('solution/<int:problem_id>/', views.submit_solution, name='submit_solution'),
    
    # URL for displaying the final solution result
    path('result/<uuid:submission_id>/', views.submission_result, name='submission_result'),
    
    #URL for handling AI suggestions
    path('ai/suggest/<int:problem_id>/', views.get_ai_suggestion, name='get_ai_suggestion'),
]