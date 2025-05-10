from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
app_name = 'superuser_portal'

urlpatterns = [
    # Dashboard and main views
    path('dashboard/', views.superuser_dashboard, name='superuser_dashboard'),
    path('manage-reservations/', views.manage_reservations, name='manage_reservations'),
    path('system-settings/', views.system_settings, name='system_settings'),
    path('user-roles/', views.user_roles, name='user_roles'),
    path('profile/', views.superuser_profile, name='superuser_profile'),
      path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Facility management
    path('facility/', views.manage_facility, name='manage_facility'),
    path('facility/<int:facility_id>/', views.manage_facility, name='edit_facility'),
    path('facility/<int:facility_id>/delete/', views.delete_facility, name='delete_facility'),
    
    # Time template management
    path('time-template/add/', views.manage_time_template, name='add_time_template'),
    path('time-template/<int:template_id>/edit/', views.manage_time_template, name='edit_time_template'),
    path('time-template/<int:template_id>/delete/', views.delete_time_template, name='delete_time_template'),
    
    # Blocked dates management
    path('blocked-dates/', views.manage_blocked_dates, name='manage_blocked_dates'),
    path('blocked-dates/<int:date_id>/delete/', views.delete_blocked_date, name='delete_blocked_date'),
    
    # User management
    path('user/<int:user_id>/change-role/', views.change_user_role, name='change_user_role'),
    path('user/<int:user_id>/reset-password/', views.reset_user_password, name='reset_user_password'),
    path('user/<int:user_id>/update-status/', views.update_user_status, name='update_user_status'),
]
