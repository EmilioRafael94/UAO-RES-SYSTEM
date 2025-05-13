from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from user_portal.forms import UserUpdateForm, ProfileUpdateForm
from user_portal.models import Reservation, BlockedDate # Make sure you have these forms imported
from django.contrib import messages
from django.utils import timezone
import json
from django.http import JsonResponse
from .models import Notification
from superuser_portal.models import BlockedDate
from django.utils.timezone import make_aware
import datetime


SAMPLE_RESERVATIONS = [
    {
        'event_name': 'Basketball Practice',
        'facility': 'Gymnasium',
        'event_date': '2025-05-05',
        'status': 'Approved',
    },
    {
        'event_name': 'Soccer Tryouts',
        'facility': 'Field',
        'event_date': '2025-05-10',
        'status': 'Pending',
    },
]

@login_required
def user_myreservation(request):
    reservations = Reservation.objects.filter(user=request.user)
    for reservation in reservations:
        print(reservation.id)  # Debug line to check if id is valid
    return render(request, 'user_portal/user_myreservation.html', {'reservations': reservations})



@login_required
def user_makereservation(request):
    today = timezone.now().date()

    if request.method == 'POST':
        organization = request.POST.get('organization')
        representative = request.POST.get('representative')
        contact_number = request.POST.get('contact_number')
        date_reserved = request.POST.get('date_reserved')
        insider_count = request.POST.get('insider_count', 0)
        outsider_count = request.POST.get('outsider_count', 0)
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        reasons = request.POST.get('reasons', '').strip()

        # Event Types
        event_types = request.POST.getlist('event_type')
        event_type = ', '.join(event_types) if event_types else 'Not specified'

        # Facility Use
        facility_use_selected = request.POST.getlist('facilities')
        facility_use = ', '.join(facility_use_selected) if facility_use_selected else 'None'

        # Facilities Needed
        facility_keys = [
            'long_tables', 'mono_block_chairs', 'narra_chairs', 'podium', 'xu_seal', 'xu_logo',
            'sound_system', 'bulletin_board', 'scaffolding', 'flag', 'philippine_flag', 'xu_flag',
            'ceiling_fans', 'stand_fans', 'iwata_fans', 'stage_non_acrylic', 'digital_clock',
            'others'
        ]
        facilities_needed = {
            key.replace('_', ' ').title(): int(request.POST.get(f"{key}_quantity", 0)) 
            for key in facility_keys 
            if request.POST.get(f"{key}_quantity")
        }

        # Manpower Needed
        manpower_keys = [
            'security', 'janitor', 'electrician', 'technician',
            'assistant_technician', 'digital_clock_operator', 'plumber', 'other_manpower'
        ]
        manpower_needed = {
            key.replace('_', ' ').title(): int(request.POST.get(f"{key}_quantity", 0)) 
            for key in manpower_keys 
            if request.POST.get(f"{key}_quantity")
        }

        # Save the reservation
        reservation = Reservation.objects.create(
            user=request.user,
            organization=organization,
            representative=representative,
            contact_number=contact_number,
            date_reserved=date_reserved,
            date=date,
            insider_count=insider_count,
            outsider_count=outsider_count,
            start_time=start_time,
            end_time=end_time,
            reasons=reasons,
            facility_use=facility_use,
            event_type=event_type,
            facilities_needed=facilities_needed,
            manpower_needed=manpower_needed,
            status="Pending",
        )

        return redirect('user_portal:user_myreservation')

    return render(request, 'user_portal/user_makereservation.html', {
        'today': today,
    })



@login_required
def edit_reservation(request, id):
    reservation = get_object_or_404(Reservation, id=id)

    if reservation.user != request.user:
        messages.error(request, "You cannot edit someone else's reservation.")
        return redirect('user_portal:user_myreservation')

    if request.method == 'POST':
        reservation.facility = request.POST.get('facility')
        reservation.date = request.POST.get('date')
        reservation.start_time = request.POST.get('start_time')
        reservation.end_time = request.POST.get('end_time')
        reservation.save()
        messages.success(request, "Reservation updated successfully!")
        return redirect('user_portal:user_myreservation')

    return render(request, 'user_portal/edit_reservation.html', {
        'reservation': reservation
    })


def delete_reservation(request, id):
    try:
        reservation = Reservation.objects.get(id=id)
        reservation.delete()
        messages.success(request, 'Reservation deleted successfully.')
    except Reservation.DoesNotExist:
        messages.error(request, 'Reservation not found.')

    return redirect('user_portal:user_myreservation')

def user_calendar(request):
    return render(request, 'user_portal/user_calendar.html')

@login_required
def user_dashboard(request):
    # Get the total, approved, and rejected reservations for the current user
    total_reservations = Reservation.objects.filter(user=request.user).count()
    approved = Reservation.objects.filter(user=request.user, status='Approved').count()
    rejected = Reservation.objects.filter(user=request.user, status='Rejected').count()

    # Fetching notifications for the current user via the related_name 'notifications' on User model
    notifications = request.user.notifications.all()

    context = {
        'total_reservations': total_reservations,
        'approved': approved,
        'rejected': rejected,
        'notifications': notifications,
    }

    return render(request, 'user_portal/user_dashboard.html', context)

@login_required
def user_profile(request):
    return render(request, 'user_portal/user_profile.html')

from django.contrib.auth.hashers import check_password
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import UserUpdateForm, ProfileUpdateForm

import base64
from django.core.files.base import ContentFile

@login_required
def update_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile = request.user.profile
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        valid_forms = user_form.is_valid() and profile_form.is_valid()
        changing_password = current_password or new_password or confirm_password

        if changing_password:
            if not (current_password and new_password and confirm_password):
                messages.error(request, 'All password fields are required to change your password.')
                valid_forms = False
            elif not check_password(current_password, request.user.password):
                messages.error(request, 'Current password is incorrect.')
                valid_forms = False
            elif new_password != confirm_password:
                messages.error(request, 'New password and confirmation do not match.')
                valid_forms = False
            elif check_password(new_password, request.user.password):
                messages.error(request, 'New password must be different from your current password.')
                valid_forms = False

        if valid_forms:
            user_form.save()
            profile_instance = profile_form.save(commit=False)

            # Handle cropped image from base64
            cropped_image_data = request.POST.get('cropped_image')
            if cropped_image_data:
                format, imgstr = cropped_image_data.split(';base64,') 
                ext = format.split('/')[-1] 
                profile_instance.profile_picture.save(
                    f'profile_{request.user.username}.{ext}',
                    ContentFile(base64.b64decode(imgstr)),
                    save=False
                )

            if profile.role != "Student of XU":
                profile_instance.course = profile.course

            profile_instance.save()

            if changing_password:
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Your profile and password have been updated successfully!')
            else:
                messages.success(request, 'Your profile has been updated successfully!')

            return redirect('user_portal:user_profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'user_portal/user_profile.html', context)



@login_required
def get_reservations(request):
    reservations = Reservation.objects.all()
    blocked = BlockedDate.objects.all()

    reservation_events = []
    for res in reservations:
        start_datetime = datetime.datetime.combine(res.date, res.start_time)
        end_datetime = datetime.datetime.combine(res.date, res.end_time)

        # If timezone-aware is needed (depends on your settings)
        try:
            start_iso = make_aware(start_datetime).isoformat()
            end_iso = make_aware(end_datetime).isoformat()
        except:
            start_iso = start_datetime.isoformat()
            end_iso = end_datetime.isoformat()
        

        reservation_events.append({
            "title": res.facility,
            "start": start_iso,
            "end": end_iso,
            "event_type": res.event_type,
            "user_name": res.user.get_full_name(),
            "organization": res.organization,
        })

    blocked_events = []
    for block in blocked:
        blocked_events.append({
            "title": f"Blocked: {block.reason}",
            "start": block.date.isoformat(),
            "end": block.date.isoformat(),
            "reason": block.reason,
        })

    return JsonResponse(reservation_events + blocked_events, safe=False)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('user_portal:user_profile')  # Redirect to profile after save
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'user_profile.html', context)

@login_required
def user_profile(request):
    user_form = UserUpdateForm(instance=request.user)
    profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'user_portal/user_profile.html', context)

def send_notification(user, message):
    notification = Notification.objects.create(user=user, message=message)
    notification.save()

# Call this function when a reservation is approved or rejected
def approve_reservation(reservation):
    reservation.status = "Approved"
    reservation.save()

    send_notification(reservation.user, f"Your reservation for {reservation.facility} has been approved.")

@login_required
def update_reservation_status(request, reservation_id, status):
    reservation = get_object_or_404(Reservation, id=reservation_id)

    if reservation.user != request.user:
        return redirect('user_portal:user_myreservation')

    reservation.status = status
    reservation.save()

    # Send a notification to the user
    send_notification(reservation.user, f"Your reservation for {reservation.facility} is now {status}.")

    return redirect('user_portal:user_myreservation')

@login_required
def upload_receipt(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    if request.method == 'POST' and request.FILES.get('receipt_file'):
        receipt = request.FILES['receipt_file']
        reservation.receipt_file = receipt
        reservation.save()
        messages.success(request, "Receipt uploaded successfully.")

    return redirect('user_portal:user_myreservation')



