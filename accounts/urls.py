from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'accounts'

class CustomLogoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('role_redirect/', views.role_redirect_view, name='role_redirect'),
    path('home/', views.home_redirect, name='home'),
    path('logout/', CustomLogoutView.as_view(next_page='accounts:login'), name='logout'),
]


