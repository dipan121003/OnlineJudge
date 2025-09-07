from django.urls import path
from . import views

app_name = 'oa_events' # This is important for namespacing URLs

urlpatterns = [
    path('', views.oa_event_list, name='oa_event_list'),
    path('<int:event_id>/', views.oa_event_detail, name='oa_event_detail'),
]