from django.urls import path
from . import views

app_name = 'admin_portal'

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('approve_reservation/<int:pk>/', views.admin_approve_reservation, name='approve_reservation'),
]
