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
    path('receipt/verify/<int:pk>/', views.verify_receipt, name='verify_receipt'),
    path('review-form/<int:pk>/', views.review_completed_form, name='review_completed_form'),
    path('reservation/<int:reservation_id>/details/', views.reservation_details, name='reservation_details'),
    path('reservation/<int:reservation_id>/details/json/', views.reservation_details_json, name='reservation_details_json'),
    
    # Fixed URL patterns for consistency
    path('billing/<int:reservation_id>/delete/', views.delete_billing, name='delete_billing'),
    path('billing/<int:reservation_id>/', views.upload_billing, name='upload_billing'),
    path('pass/<int:reservation_id>/', views.upload_security_pass, name='upload_security_pass'),
    path('reservation/<int:reservation_id>/reject/', views.reject_reservation, name='reject_reservation'),
    path('settings/', views.system_settings, name='system_settings'),
    path('settings/blocked-dates/', views.get_blocked_dates, name='get_blocked_dates'),
    path('settings/add-blocked-date/', views.add_blocked_date, name='add_blocked_date'),

    # AJAX endpoints for billing and security pass actions
    path('edit_billing_file/<int:reservation_id>/', views.edit_billing_file, name='edit_billing_file'),
    path('delete_billing_file/<int:reservation_id>/', views.delete_billing_file, name='delete_billing_file'),
    path('edit_security_pass/<int:reservation_id>/', views.edit_security_pass, name='edit_security_pass'),
    path('delete_security_pass/<int:reservation_id>/', views.delete_security_pass, name='delete_security_pass'),
    path('approve_security_pass/<int:reservation_id>/', views.approve_security_pass, name='approve_security_pass'),
    path('delete_user_receipt/<int:reservation_id>/', views.delete_user_receipt, name='delete_user_receipt'),
    path('delete_user_completed_form/<int:reservation_id>/', views.delete_user_completed_form, name='delete_user_completed_form'),
]