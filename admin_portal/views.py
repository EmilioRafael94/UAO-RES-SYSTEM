from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.contrib import messages
from datetime import datetime
from .models import Profile
from reservations.models import Reservation
from user_portal.models import Notification

def is_admin(user):
    return user.is_staff or user.is_superuser

# Admin Dashboard View
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Get all pending reservations
    pending = Reservation.objects.filter(status='Pending').order_by('-date')
    pending_count = pending.count()

    # Get reservations approved by this specific admin
    approved = Reservation.objects.filter(
        admin_approvals__has_key=request.user.username
    ).order_by('-date')[:5]  # Show last 5 approved

    # Get all rejected reservations (keeping it as it was before)
    rejected = Reservation.objects.filter(status='Rejected').order_by('-date')[:10]

    # Get selected reservation if ID is provided
    selected_reservation = None
    reservation_id = request.GET.get('id')
    if reservation_id:
        selected_reservation = get_object_or_404(Reservation, id=reservation_id)

    context = {
        'pending': pending,
        'pending_count': pending_count,
        'approved': approved,
        'rejected': rejected,
        'selected_reservation': selected_reservation,
    }
    return render(request, 'admin_portal/admin_dashboard.html', context)

# Approve Reservation View
@login_required
@user_passes_test(is_admin)
def approve_reservation(request, reservation_id):
    if request.method == 'POST':
        reservation = get_object_or_404(Reservation, id=reservation_id)
        admin_notes = request.POST.get('admin_notes', '').strip()
        admin_username = request.user.username

        # Add admin approval
        reservation.add_admin_approval(admin_username, admin_notes)

        # Ensure the reservation status is updated to 'Admin Approved' if it meets the criteria
        if len(reservation.admin_approvals) >= 4:
            reservation.status = 'Admin Approved'
            reservation.save()

        # Create notification for the user about approval
        Notification.objects.create(
            user=reservation.user,
            message=f"Your reservation for {reservation.facility_use} on {reservation.date} has been approved by {admin_username}. {admin_notes if admin_notes else ''}",
            notification_type='reservation_approved'
        )
        
        messages.success(request, f"Reservation for {reservation.facility_use} approved by {admin_username}.")
    return redirect('admin_portal:admin_dashboard')

# Reject Reservation View
@login_required
@user_passes_test(is_admin)
def reject_reservation(request, reservation_id):
    if request.method == 'POST':
        reservation = get_object_or_404(Reservation, id=reservation_id)
        rejection_reason = request.POST.get('rejection_reason', '').strip()
        admin_username = request.user.username

        if not rejection_reason:
            messages.error(request, "Please provide a reason for rejection.")
            return redirect('admin_portal:admin_dashboard')

        # Add admin rejection
        reservation.add_admin_rejection(admin_username, rejection_reason)

        # Create notification for the user about rejection
        Notification.objects.create(
            user=reservation.user,
            message=f"Your reservation for {reservation.facility_use} on {reservation.date} has been rejected. Reason: {rejection_reason}",
            notification_type='reservation_rejected'
        )
        
        messages.success(request, f"Reservation for {reservation.facility_use} rejected.")
    return redirect('admin_portal:admin_dashboard')

# Admin Calendar View
@login_required
@user_passes_test(is_admin)
def calendar_view(request):
    reservations = get_approved_reservations(request)  # Ensure this is only approved reservations
    return render(request, 'admin_portal/calendar.html', {'reservations': reservations})

# Fetch Approved Reservations for Calendar
@login_required
@user_passes_test(is_admin)
def get_approved_reservations(request):
    reservations = Reservation.objects.filter(status='Completed')
    events = []

    for res in reservations:
        start_datetime = datetime.combine(res.date, res.start_time)
        end_datetime = datetime.combine(res.date, res.end_time)
        events.append({
            'id': res.id,
            'title': f"{res.facility} ({res.user.username})",
            'start': start_datetime.isoformat(),
            'end': end_datetime.isoformat(),
            'extendedProps': {
                'organization': res.organization,
                'representative': res.representative,
                'event_type': res.event_type,
                'insider_count': res.insider_count,
                'outsider_count': res.outsider_count,
                'status': res.status,
            }
        })
    return JsonResponse(events, safe=False)

# Admin Profile View
@login_required
@user_passes_test(is_admin)
def admin_profile(request):
    profile = Profile.objects.filter(user=request.user).first()
    return render(request, 'admin_portal/admin_profile.html', {'profile': profile})

# Update Admin Profile
@login_required
@user_passes_test(is_admin)
def update_profile(request):
    if request.method == 'POST':
        # Get the form data from POST request
        name = request.POST.get('name')
        email = request.POST.get('email')
        course = request.POST.get('course')
        phone = request.POST.get('phone')
        
        # Update the user model
        user = request.user
        name_parts = name.split(maxsplit=1)
        user.first_name = name_parts[0]
        user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        user.email = email
        user.save()
        
        # Update the profile model (ensure that Profile exists for each user)
        profile, created = Profile.objects.get_or_create(user=user)
        profile.course = course
        profile.phone = phone
        profile.save()
        
        # Redirect back to the profile page after update
        messages.success(request, "Profile updated successfully!")
        return redirect('admin_portal:admin_profile')
    
    # If not POST, redirect back to the profile page
    return redirect('admin_portal:admin_profile')
