from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from user_portal.forms import UserUpdateForm, ProfileUpdateForm
from reservations.models import Reservation  # Changed from user_portal.models to reservations.models
from django.contrib import messages
from django.utils import timezone
import json
from django.http import JsonResponse
from .models import Notification


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
        # Debug: Print all POST data
        print("\n=== Form Submission Data ===")
        for key, value in request.POST.items():
            print(f"{key}: {value}")
        print("===========================\n")

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

        # Facility (single selection)
        facility = request.POST.get('facility')
        facility_use = facility

        # Event Types (checkboxes, allow multiple)
        event_types = request.POST.getlist('event_type')
        if not event_types:
            messages.error(request, 'Please select at least one event type')
            return redirect('user_portal:user_makereservation')
        event_type = ', '.join(event_types)

        # Validate required fields
        required_fields = [facility, organization, representative, date, start_time, end_time, event_type]
        if not all(required_fields):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('user_portal:user_makereservation')

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

        try:
            # Debug: Print reservation data before creation
            print("\n=== Creating Reservation ===")
            print(f"User: {request.user.username}")
            print(f"Date: {date}")
            print(f"Start Time: {start_time}")
            print(f"End Time: {end_time}")
            print(f"Facility: {facility}")
            print(f"Status: Pending")
            print("==========================\n")

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
                facility=facility,
                facility_use=facility_use,
                event_type=event_type,
                facilities_needed=facilities_needed,
                manpower_needed=manpower_needed,
                status="Pending",
            )
            
            # Debug: Print success message
            print(f"\n=== Reservation Created Successfully ===")
            print(f"Reservation ID: {reservation.id}")
            print("=====================================\n")
            
            messages.success(request, 'Reservation created successfully!')
        except Exception as e:
            # Debug: Print error details
            print(f"\n=== Error Creating Reservation ===")
            print(f"Error: {str(e)}")
            print("===============================\n")
            
            messages.error(request, f'Error creating reservation: {str(e)}')
            return redirect('user_portal:user_makereservation')

        return redirect('user_portal:user_myreservation')

    return render(request, 'user_portal/user_makereservation.html', {
        'today': today,
    })



@login_required
def edit_reservation(request, id):
    reservation = get_object_or_404(Reservation, pk=id)

    if request.method == 'POST':
        reservation.date = request.POST.get('date')
        reservation.start_time = request.POST.get('start_time')
        reservation.end_time = request.POST.get('end_time')

        # Update facilities to be used
        facilities = request.POST.getlist('facility_use')  # Name should match the checkbox name
        reservation.facility_use = ", ".join(facilities)

        # Update facilities needed
        reservation.facilities_needed = {
            'long_tables': int(request.POST.get('long_tables_quantity') or 0),
            'mono_block_chairs': int(request.POST.get('mono_block_chairs_quantity') or 0),
            'narra_chairs': int(request.POST.get('narra_chairs_quantity') or 0),
            'podium': int(request.POST.get('podium_quantity') or 0),
            'xu_seal': int(request.POST.get('xu_seal_quantity') or 0),
            'xu_logo': int(request.POST.get('xu_logo_quantity') or 0),
            'sound_system': int(request.POST.get('sound_system_quantity') or 0),
            'bulletin_board': int(request.POST.get('bulletin_board_quantity') or 0),
            'scaffolding': int(request.POST.get('scaffolding_quantity') or 0),
            'flag': int(request.POST.get('flag_quantity') or 0),
            'philippine_flag': int(request.POST.get('philippine_flag_quantity') or 0),
            'xu_flag': int(request.POST.get('xu_flag_quantity') or 0),
            'ceiling_fans': int(request.POST.get('ceiling_fans_quantity') or 0),
            'stand_fans': int(request.POST.get('stand_fans_quantity') or 0),
            'iwata_fans': int(request.POST.get('iwata_fans_quantity') or 0),
            'stage_non_acrylic': int(request.POST.get('stage_non_acrylic_quantity') or 0),
            'digital_clock': int(request.POST.get('digital_clock_quantity') or 0),
            'others': request.POST.get('others_specify', ''),
        }

        # Update manpower needed
        reservation.manpower_needed = {
            'security': int(request.POST.get('security_quantity') or 0),
            'janitor': int(request.POST.get('janitor_quantity') or 0),
            'electrician': int(request.POST.get('electrician_quantity') or 0),
            'technician': int(request.POST.get('technician_quantity') or 0),
            'assistant_technician': int(request.POST.get('assistant_technician_quantity') or 0),
            'digital_clock_operator': int(request.POST.get('digital_clock_operator_quantity') or 0),
            'plumber': int(request.POST.get('plumber_quantity') or 0),
            'other': int(request.POST.get('other_manpower_quantity') or 0),
        }

        reservation.save()
        return redirect('user_portal:user_myreservation')

    # Prepopulate facility_use as list
    facilities_list = reservation.facility_use.split(', ') if reservation.facility_use else []

    # Prepare facilities_quantity and manpower_quantity dictionaries
    facilities_quantity = reservation.facilities_needed if reservation.facilities_needed else {}
    manpower_quantity = reservation.manpower_needed if reservation.manpower_needed else {}

    return render(request, 'user_portal/edit_reservation.html', {
        'reservation': reservation,
        'facilities_list': facilities_list,  # for checked checkboxes
        'facilities_quantity': facilities_quantity,  # for facilities quantities
        'manpower_quantity': manpower_quantity,  # for manpower quantities
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

# USER DASHBOARD VIEW
@login_required
def user_dashboard(request):
    user_reservations = Reservation.objects.filter(user=request.user)
    
    # Only show pending reservations that haven't been approved/rejected
    pending_reservations = user_reservations.filter(status='Pending')
    
    # Only show approved reservations that are upcoming
    upcoming_reservations = user_reservations.filter(
        status='Approved',
        date__gte=timezone.now().date()
    ).order_by('date', 'start_time')
    
    # Add formatted time to each reservation
    for reservation in pending_reservations:
        reservation.formatted_time = f"{reservation.start_time.strftime('%I:%M %p')} - {reservation.end_time.strftime('%I:%M %p')}"
    
    for reservation in upcoming_reservations:
        reservation.formatted_time = f"{reservation.start_time.strftime('%I:%M %p')} - {reservation.end_time.strftime('%I:%M %p')}"
    
    context = {
        'pending_reservations': pending_reservations,
        'upcoming_reservations': upcoming_reservations,
        'notifications': request.user.notifications.all(),
    }
    return render(request, 'user_portal/user_dashboard.html', context)

# chatgpt ----------------------------------------------------------------------------------
@login_required
def get_user_calendar_events(request):
    approved_reservations = Reservation.objects.filter(user=request.user, status='Approved')
    
    events = []
    for reservation in approved_reservations:
        events.append({
            'id': reservation.id,
            'title': f"{reservation.facility_use} - {reservation.organization}",
            'start': f"{reservation.date}T{reservation.start_time}",
            'end': f"{reservation.date}T{reservation.end_time}",
            'extendedProps': {
                'organization': reservation.organization,
                'representative': reservation.representative,
                'event_type': reservation.event_type,
                'insider_count': reservation.insider_count,
                'outsider_count': reservation.outsider_count,
                'facilities_needed': reservation.facilities_needed,
                'manpower_needed': reservation.manpower_needed,
                'admin_notes': reservation.admin_notes,
                'time_slot': reservation.time_slot
            }
        })
    
    return JsonResponse(events, safe=False)


@login_required
def update_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile = request.user.profile
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()

            profile_instance = profile_form.save(commit=False)

            if profile.role != "Student of XU":
                profile_instance.course = profile.course  # keep existing course (if any)

            profile_instance.save()

            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('user_portal:user_profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'user_profile.html', context)

@login_required
def get_reservations(request):
    # Only get approved reservations for the calendar
    reservations = Reservation.objects.filter(status='Approved')
    
    events = []
    for r in reservations:
        # Convert facilities_needed to a string with quantities (assuming it's a dictionary)
        facilities_list = []
        if isinstance(r.facilities_needed, dict):
            for facility, quantity in r.facilities_needed.items():
                facilities_list.append(f"{facility}: {quantity}")
        else:
            facilities_list.append('None')

        # Convert manpower_needed to a string with quantities (assuming it's a dictionary)
        manpower_list = []
        if isinstance(r.manpower_needed, dict):
            for manpower, quantity in r.manpower_needed.items():
                manpower_list.append(f"{manpower}: {quantity}")
        else:
            manpower_list.append('None')

        events.append({
            'title': r.facility_use,  # assuming facility_use is a string
            'start': f"{r.date}T{r.start_time}",
            'end': f"{r.date}T{r.end_time}",
            'event_type': r.event_type,
            'facilities_needed': ', '.join(facilities_list) if facilities_list else 'None',
            'manpower_needed': ', '.join(manpower_list) if manpower_list else 'None',
        })
    
    return JsonResponse(events, safe=False)

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