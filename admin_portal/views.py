from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from reservations.models import Reservation
from reservations.views import approve_reservation

@login_required
def admin_dashboard(request):
    pending = Reservation.objects.filter(status='pending')
    approved = Reservation.objects.filter(status='approved')
    selected_reservation = pending.first()  # Default reservation to show in the card

    return render(request, 'admin_dashboard.html', {
        'pending': pending,
        'approved': approved,
        'selected_reservation': selected_reservation,
    })

@login_required
def admin_approve_reservation(request, pk):
    return approve_reservation(request, pk)

@login_required
def dashboard(request):
    return render(request, 'admin_portal/dashboard.html')
