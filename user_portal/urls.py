from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'user_portal'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.user_dashboard, name='user_dashboard'),

    # Profile and profile update
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),

    # Calendar and events
    path('calendar/', views.user_calendar, name='user_calendar'),
    path('api/calendar-events/', views.get_user_calendar_events, name='user_calendar_events'),

    # Reservation actions
    path('make-reservation/', views.user_makereservation, name='user_makereservation'),
    path('my-reservations/', views.user_myreservation, name='user_myreservation'),
    path('edit-reservation/<int:id>/', views.edit_reservation, name='edit_reservation'),
    path('delete-reservation/<int:id>/', views.delete_reservation, name='delete_reservation'),

    # Get user reservations
    path('get-reservations/', views.get_reservations, name='get_reservations'),

    # Logout
    path('logout/', LogoutView.as_view(), name='logout'),
]
