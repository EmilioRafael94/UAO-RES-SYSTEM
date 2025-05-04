from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from reservations.models import Reservation
from reservations.views import approve_reservation

@login_required
def admin_dashboard(request):
    # Fetch the pending and approved reservations
    pending = Reservation.objects.filter(status='pending')
    approved = Reservation.objects.filter(status='approved')

    # Default reservation to show in the card
    selected_reservation = pending.first()

    # Return the dashboard view with reservations data
    return render(request, 'admin_portal/admin_dashboard.html', {
        'pending': pending,
        'approved': approved,
        'selected_reservation': selected_reservation,
    })

@login_required
def admin_approve_reservation(request, pk):
    # Redirect to the approval function
    return approve_reservation(request, pk)

@login_required
def calendar_view(request):
    # Render the calendar view
    return render(request, 'admin_portal/calendar.html')
