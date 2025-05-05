from django.shortcuts import render
from reservations.views import finalize_reservation
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from reservations.models import Reservation
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test

# Superuser check function
def is_superuser(user):
    return user.is_superuser

@login_required
@user_passes_test(is_superuser)
def superuser_profile(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('superuser_portal:superuser_profile')  # Redirect to the same page after saving
    else:
        form = UserChangeForm(instance=request.user)

    return render(request, 'superuser/superuser_profile.html', {'form': form})

def is_superuser(user):
    return user.is_superuser
@login_required
@user_passes_test(is_superuser)
def system_settings(request):
    return render(request, 'superuser/superuser_systemsettings.html')

def is_superuser(user):
    return user.is_superuser

@login_required
@user_passes_test(is_superuser)
def user_roles(request):
    users = User.objects.all()
    return render(request, 'superuser/superuser_userroles.html', {'users': users})

# Optional: Limit to superusers
def is_superuser(user):
    return user.is_superuser

@login_required
@user_passes_test(is_superuser)
def manage_reservations(request):
    return render(request, 'superuser/superuser_managereservations.html')

@login_required
@user_passes_test(is_superuser)
def superuser_dashboard(request):
    admins = User.objects.filter(is_staff=True).exclude(is_superuser=True)
    reservations = Reservation.objects.all()

    return render(request, 'superuser/superuser_dashboard.html', {
        'admins': admins,
        'reservations': reservations
    })

def superuser_finalize_reservation(request, pk):
    return finalize_reservation(request, pk)

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

