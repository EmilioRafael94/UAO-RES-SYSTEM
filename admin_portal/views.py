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

def admin_profile(request):
    return render(request, 'admin_portal/admin_profile.html')

def update_profile(request):
    if request.method == 'POST':
        # Get the form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        course = request.POST.get('course')
        phone = request.POST.get('phone')
        
        # Update the user
        user = request.user
        # Split the name into first_name and last_name
        name_parts = name.split(maxsplit=1)
        user.first_name = name_parts[0]
        user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        user.email = email
        user.save()
        
        # Update the profile
        # Note: You'll need to ensure you have a Profile model
        # If you don't have one, you'll need to create it
        profile, created = Profile.objects.get_or_create(user=user)
        profile.course = course
        profile.phone = phone
        profile.save()
        
        # Redirect back to the profile page
        return redirect('admin_portal:admin_profile')
    
    # If not POST, redirect back to profile
    return redirect('admin_portal:admin_profile')
