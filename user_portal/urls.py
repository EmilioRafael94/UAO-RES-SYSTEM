from django.urls import path
from . import views

app_name = 'user_portal'

urlpatterns = [
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('make_reservation/', views.user_reservation, name='make_reservation'),
]
