from django.urls import path
from . import views

app_name = 'user_portal'  # This matches the namespace used in your views

urlpatterns = [
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('profile/', views.user_profile, name='user_profile'),
    path('calendar/', views.user_calendar, name='user_calendar'),
    path('reservations/', views.user_myreservation, name='user_myreservation'),
    path('reservations/make/', views.user_makereservation, name='user_makereservation'),
    path('reservations/edit/<int:id>/', views.edit_reservation, name='edit_reservation'),
    path('reservations/delete/<int:id>/', views.delete_reservation, name='delete_reservation'),
    path('reservations/upload-receipt/<int:reservation_id>/', views.upload_receipt, name='upload_receipt'),
    path('reservations/upload-security-pass/<int:reservation_id>/', views.upload_security_pass, name='upload_security_pass'),
    path('calendar/events/', views.get_user_calendar_events, name='get_user_calendar_events'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('reservations/get/', views.get_reservations, name='get_reservations'),
    path('reservations/check-date/', views.check_date_availability, name='check_date_availability'),
]
