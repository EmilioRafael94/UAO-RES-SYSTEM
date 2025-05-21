from django.shortcuts import redirect
from social_core.exceptions import AuthForbidden

def social_auth_forbidden(backend, *args, **kwargs):
    # This pipeline step is only called if AuthForbidden is raised
    return redirect('/accounts/login/?error=forbidden')
