from django.urls import path
from . import views

app_name = 'superuser_portal'

urlpatterns = [
    # Dashboard and main views
    path('dashboard/', views.superuser_dashboard, name='superuser_dashboard'),
    path('manage-reservations/', views.manage_reservations, name='manage_reservations'),
    path('system-settings/', views.system_settings, name='system_settings'),
    path('user-roles/', views.user_roles, name='user_roles'),
    path('profile/', views.superuser_profile, name='superuser_profile'),
    
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
    path('reservation/<int:reservation_id>/details/', views.reservation_details, name='reservation_details'),
    path('upload-billing/<int:reservation_id>/', views.upload_billing, name='upload_billing'),
    path('upload_billing/<int:reservation_id>/', views.upload_billing_statement, name='upload_billing'),
    path('verify_payment/<int:reservation_id>/', views.verify_payment, name='verify_payment'),
    path('reservation/<int:reservation_id>/upload-security-pass/', views.upload_security_pass, name='upload_security_pass'),
    path('reservation/<int:reservation_id>/confirm-security-pass/', views.confirm_security_pass, name='confirm_security_pass'),
    path('reservation/<int:reservation_id>/reject-security-pass/', views.reject_security_pass, name='reject_security_pass'),
]



