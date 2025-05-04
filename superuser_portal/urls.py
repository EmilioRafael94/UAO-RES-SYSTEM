from django.urls import path
from . import views

app_name = 'superuser_portal'

urlpatterns = [
    path('dashboard/', views.superuser_dashboard, name='superuser_dashboard'),
    path('finalize_reservation/<int:pk>/', views.superuser_finalize_reservation, name='finalize_reservation'),
]
