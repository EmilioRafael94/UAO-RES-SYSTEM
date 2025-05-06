from django.urls import path
from . import views

app_name = 'admin_portal'

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('profile/', views.admin_profile, name='admin_profile'),
    path('update_profile/', views.update_profile, name='update_profile'),
]