from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'user_portal'

urlpatterns = [
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('calendar/', views.user_calendar, name='user_calendar'),
    path('make-reservation/', views.user_makereservation, name='user_makereservation'),
    path('my-reservations/', views.user_myreservation, name='user_myreservation'),
    path('edit/<int:id>/', views.edit_reservation, name='edit_reservation'),
    path('delete/<int:id>/', views.delete_reservation, name='delete_reservation'),
    path('get-reservations/', views.get_reservations, name='get_reservations'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('upload-receipt/<int:reservation_id>/', views.upload_receipt, name='upload_receipt'),
    path('reservations/', views.my_reservations, name='my_reservations'),
    path('upload-completed-form/<int:reservation_id>/', views.upload_completed_form, name='upload_completed_form'),
    path('reservation/<int:reservation_id>/', views.view_reservation_details, name='view_reservation_details'),



]
