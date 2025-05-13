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
    # Debug: Print all reservations
    print("\n=== All Reservations ===")
    all_reservations = Reservation.objects.all()
    for res in all_reservations:
        print(f"ID: {res.id}, User: {res.user.username}, Status: {res.status}, Date: {res.date}")
    print("=======================\n")

    # Fetch pending and approved reservations
    pending_reservations = Reservation.objects.filter(status='Pending').order_by('-date', '-created_at')
    approved_reservations = Reservation.objects.filter(status='Approved').order_by('-date', '-created_at')[:10]

    # Debug: Print filtered reservations
    print("\n=== Pending Reservations ===")
    for res in pending_reservations:
        print(f"ID: {res.id}, User: {res.user.username}, Date: {res.date}")
    print("===========================\n")

    print("\n=== Approved Reservations ===")
    for res in approved_reservations:
        print(f"ID: {res.id}, User: {res.user.username}, Date: {res.date}")
    print("============================\n")

    # Handle selected reservation if it exists, otherwise default to the first pending reservation
    selected_reservation_id = request.GET.get('id')
    selected_reservation = None
    if selected_reservation_id:
        selected_reservation = Reservation.objects.filter(id=selected_reservation_id).first()
    if not selected_reservation and pending_reservations.exists():
        selected_reservation = pending_reservations.first()

    context = {
        'pending': pending_reservations,
        'approved': approved_reservations,
        'selected_reservation': selected_reservation,
        'pending_count': pending_reservations.count(),
    }
    
    return render(request, 'admin_portal/admin_dashboard.html', context)

# Approve Reservation View
@login_required
@user_passes_test(is_admin)
def approve_reservation(request, reservation_id):
    if request.method == 'POST':
        reservation = get_object_or_404(Reservation, id=reservation_id)
        admin_notes = request.POST.get('admin_notes', '').strip()
        
        # Update reservation status
        reservation.status = 'Approved'
        if admin_notes:
            reservation.admin_notes = admin_notes
        reservation.save()

        # Create notification for the user
        Notification.objects.create(
            user=reservation.user,
            message=f"Your reservation for {reservation.facility_use} on {reservation.date} has been approved. {admin_notes if admin_notes else ''}",
            notification_type='reservation_approved'
        )
        
        messages.success(request, f"Reservation for {reservation.facility_use} approved.")
    return redirect('admin_portal:admin_dashboard')

# Reject Reservation View
@login_required
@user_passes_test(is_admin)
def reject_reservation(request, reservation_id):
    if request.method == 'POST':
        reservation = get_object_or_404(Reservation, id=reservation_id)
        rejection_reason = request.POST.get('rejection_reason', '').strip()
        
        # Update reservation status
        reservation.status = 'Rejected'
        if rejection_reason:
            reservation.rejection_reason = rejection_reason
        reservation.save()

        # Create notification for the user
        Notification.objects.create(
            user=reservation.user,
            message=f"Your reservation for {reservation.facility_use} on {reservation.date} has been rejected. Reason: {rejection_reason if rejection_reason else 'No reason provided'}",
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
    reservations = Reservation.objects.filter(status='Approved')
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
