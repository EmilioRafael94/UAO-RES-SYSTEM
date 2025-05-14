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
    
    path('pending/', views.pending_reservations, name='pending_reservations'),
    path('approve/<int:pk>/', views.approve_reservation, name='approve_reservation'),
    path('billing/<int:reservation_id>/', views.upload_billing, name='upload_billing'),
    path('receipt/verify/<int:pk>/', views.verify_receipt, name='verify_receipt'),
    path('review-form/<int:pk>/', views.review_completed_form, name='review_completed_form'),
    path('reservation/<int:reservation_id>/details/', views.reservation_details, name='reservation_details'),
    path('reservation/<int:reservation_id>/details/json/', views.reservation_details_json, name='reservation_details_json'),
    path('reservation/<int:reservation_id>/reject/', views.reject_reservation, name='reject_reservation'),
    
    # Fixed URL patterns for consistency
    path('pass/<int:reservation_id>/', views.upload_security_pass, name='upload_security_pass'),
    path('billing/<int:reservation_id>/delete/', views.delete_billing, name='delete_billing'),
    path('settings/', views.system_settings, name='system_settings'),
    path('settings/blocked-dates/', views.get_blocked_dates, name='get_blocked_dates'),
    path('settings/add-blocked-date/', views.add_blocked_date, name='add_blocked_date'),



]