from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import home_redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('user_portal.urls')),
    path('admin_portal/', include('admin_portal.urls')),
    path('superuser_portal/', include('superuser_portal.urls')),
    path('', home_redirect, name='home'),
    path('accounts/', include('accounts.urls', namespace='accounts')),  
    path('oauth/', include('social_django.urls', namespace='social')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
