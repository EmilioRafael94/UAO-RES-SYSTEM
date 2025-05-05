from django.urls import path
from . import views

app_name = 'superuser_portal'

urlpatterns = [
    path('dashboard/', views.superuser_dashboard, name='superuser_dashboard'),
    path('finalize_reservation/<int:pk>/', views.superuser_finalize_reservation, name='finalize_reservation'),
    path('manage-reservations/', views.manage_reservations, name='manage_reservations'),
    path('user-roles/', views.user_roles, name='user_roles'),
    path('system-settings/', views.system_settings, name='system_settings'),

]
