from django.shortcuts import redirect
from social_core.exceptions import AuthForbidden
from user_portal.models import Profile
from django.contrib import messages

def restrict_email_domain(backend, details, response, *args, **kwargs):
    email = details.get('email')
    if not email or not email.endswith('@my.xu.edu.ph'):
        return redirect('accounts:google_auth_forbidden')

def create_profile_if_not_exists(backend, user, *args, **kwargs):
    if not hasattr(user, 'profile'):
        Profile.objects.create(user=user, role='Student of XU', is_verified=True)
