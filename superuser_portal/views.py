from django.shortcuts import render
from reservations.views import finalize_reservation
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from reservations.models import Reservation
@login_required
def superuser_dashboard(request):
    # Fetch admins (users who are staff but not superusers)
    admins = User.objects.filter(is_staff=True).exclude(is_superuser=True)
    
    # Fetch all reservations
    reservations = Reservation.objects.all()

    return render(request, 'superuser_dashboard.html', {
        'admins': admins,
        'reservations': reservations
    })
def superuser_finalize_reservation(request, pk):
    return finalize_reservation(request, pk)

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

