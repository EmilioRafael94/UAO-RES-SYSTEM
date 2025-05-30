from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.contrib import messages
from datetime import datetime
from .models import Profile
from reservations.models import Reservation
from user_portal.models import Notification
from reservations.email_utils import send_reservation_email
from superuser_portal.models import BlockedDate

def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    pending = Reservation.objects.filter(status='Pending').order_by('-date')
    pending_count = pending.count()

    approved = Reservation.objects.filter(
        admin_approvals__has_key=request.user.username
    ).order_by('-date')[:5]

    rejected = Reservation.objects.filter(status='Rejected').order_by('-date')[:10]

    selected_reservation = None
    reservation_id = request.GET.get('id')
    if reservation_id and reservation_id.isdigit():
        selected_reservation = get_object_or_404(Reservation, id=reservation_id)

    context = {
        'pending': pending,
        'pending_count': pending_count,
        'approved': approved,
        'rejected': rejected,
        'selected_reservation': selected_reservation,
    }
    return render(request, 'admin_portal/admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def approve_reservation(request, reservation_id):
    if request.method == 'POST':
        reservation = get_object_or_404(Reservation, id=reservation_id)
        admin_notes = request.POST.get('admin_notes', '').strip()
        admin_username = request.user.username

        reservation.add_admin_approval(admin_username, admin_notes)

        if len(reservation.admin_approvals) >= 4:
            reservation.status = 'Admin Approved'
            reservation.save()
            send_reservation_email(
                reservation.user,
                'Reservation Approved by Admins',
                'reservation_approved_admins_email.html',
                {'subject': 'Reservation Approved by Admins', 'user': reservation.user, 'reservation': reservation}
            )

        Notification.objects.create(
            user=reservation.user,
            message=f"Your reservation for {reservation.facility_use} on {reservation.date} has been approved by {admin_username}. {admin_notes if admin_notes else ''}",
            notification_type='reservation_approved'
        )
        
        messages.success(request, f"Reservation for {reservation.facility_use} approved by {admin_username}.")
    return redirect('admin_portal:admin_dashboard')

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

        reservation.add_admin_rejection(admin_username, rejection_reason)

        send_reservation_email(
            reservation.user,
            'Reservation Rejected',
            'reservation_rejected_email.html',
            {'subject': 'Reservation Rejected', 'user': reservation.user, 'reservation': reservation}
        )

        Notification.objects.create(
            user=reservation.user,
            message=f"Your reservation for {reservation.facility_use} on {reservation.date} has been rejected. Reason: {rejection_reason}",
            notification_type='reservation_rejected'
        )
        
        messages.success(request, f"Reservation for {reservation.facility_use} rejected.")
    return redirect('admin_portal:admin_dashboard')

@login_required
@user_passes_test(is_admin)
def calendar_view(request):
    reservations = get_approved_reservations(request)
    return render(request, 'admin_portal/calendar.html', {'reservations': reservations})

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

    for bd in BlockedDate.objects.all():
        events.append({
            'title': f"{bd.facility.name} (Blocked)",
            'start': f"{bd.date}T{bd.start_time}",
            'end': f"{bd.date}T{bd.end_time}",
            'color': '#dc3545',
            'event_type': 'Blocked',
            'reason': bd.reason
        })

    return JsonResponse(events, safe=False)

@login_required
@user_passes_test(is_admin)
def admin_profile(request):
    profile = Profile.objects.filter(user=request.user).first()
    return render(request, 'admin_portal/admin_profile.html', {'profile': profile})

@login_required
@user_passes_test(is_admin)
def update_profile(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        course = request.POST.get('course')
        phone = request.POST.get('phone')
        
        user = request.user
        name_parts = name.split(maxsplit=1)
        user.first_name = name_parts[0]
        user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        user.email = email
        user.save()
        
        profile, created = Profile.objects.get_or_create(user=user)
        profile.course = course
        profile.phone = phone
        profile.save()
        
        messages.success(request, "Profile updated successfully!")
        return redirect('admin_portal:admin_profile')
    
    return redirect('admin_portal:admin_profile')
