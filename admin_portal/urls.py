from django.urls import path
from . import views

app_name = 'admin_portal'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Calendar
    path('calendar/', views.calendar_view, name='calendar'),
    path('api/calendar-events/', views.get_approved_reservations, name='admin_calendar_events'),
    path('calendar/', views.calendar_view, name='calendar_view'),

    # Reservation actions
    path('approve/<int:reservation_id>/', views.approve_reservation, name='approve_reservation'),
    path('reject/<int:reservation_id>/', views.reject_reservation, name='reject_reservation'),
    path('get_approved_reservations/', views.get_approved_reservations, name='get_all_reservations'),

    # Admin profile
    path('profile/', views.admin_profile, name='admin_profile'),
    path('update_profile/', views.update_profile, name='update_profile'),
]


