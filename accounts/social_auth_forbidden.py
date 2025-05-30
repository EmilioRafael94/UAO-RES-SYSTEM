from django.shortcuts import redirect
from social_core.exceptions import AuthForbidden

def social_auth_forbidden(backend, *args, **kwargs):
    return redirect('/accounts/login/?error=forbidden')

def forbidden_by_email(strategy, details, backend, *args, **kwargs):
    """
    Social Auth pipeline function to restrict Google login to @my.xu.edu.ph only.
    Redirects to a friendly error page if not allowed.
    """
    email = details.get('email', '')
    if not email.endswith('@my.xu.edu.ph'):
        return redirect('accounts:google_auth_forbidden')
    return None
