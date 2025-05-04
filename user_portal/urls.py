from django.urls import path
from . import views

app_name = 'user_portal'

urlpatterns = [
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
]
