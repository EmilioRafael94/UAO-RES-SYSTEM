from django.urls import path
from . import views

app_name = 'admin_portal'

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('calendar/', views.calendar_view, name='calendar'),
    path('api/calendar-events/', views.get_approved_reservations, name='admin_calendar_events'),
    path('calendar/', views.calendar_view, name='calendar_view'),

    path('approve/<int:reservation_id>/', views.approve_reservation, name='approve_reservation'),
    path('reject/<int:reservation_id>/', views.reject_reservation, name='reject_reservation'),
    path('get_approved_reservations/', views.get_approved_reservations, name='get_all_reservations'),

    path('profile/', views.admin_profile, name='admin_profile'),
    path('update_profile/', views.update_profile, name='update_profile'),
]
