from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from user_portal.forms import UserUpdateForm, ProfileUpdateForm
from reservations.models import Reservation  # Changed from user_portal.models to reservations.models
from django.contrib import messages
from django.utils import timezone
import json
from django.http import JsonResponse
from .models import Notification
from django.contrib.auth.models import User
from django.conf import settings
import os
from datetime import datetime, time
from datetime import datetime  # Import datetime for time comparison


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
    context = {}

    if request.method == 'POST':
        # Get all form data
        form_data = {
            'organization': request.POST.get('organization'),
            'representative': request.POST.get('representative'),
            'contact_number': request.POST.get('contact_number'),
            'date_reserved': request.POST.get('date_reserved'),
            'insider_count': request.POST.get('insider_count', 0),
            'outsider_count': request.POST.get('outsider_count', 0),
            'facility': request.POST.get('facility'),
            'facility_use': request.POST.getlist('facility_use'),
            'event_type': request.POST.getlist('event_type'),
            'reasons': request.POST.get('reasons', ''),
            
            # Add quantities for facilities
            'long_tables_quantity': request.POST.get('long_tables_quantity', 0),
            'mono_block_chairs_quantity': request.POST.get('mono_block_chairs_quantity', 0),
            'narra_chairs_quantity': request.POST.get('narra_chairs_quantity', 0),
            'podium_quantity': request.POST.get('podium_quantity', 0),
            'xu_seal_quantity': request.POST.get('xu_seal_quantity', 0),
            'xu_logo_quantity': request.POST.get('xu_logo_quantity', 0),
            'sound_system_quantity': request.POST.get('sound_system_quantity', 0),
            'bulletin_board_quantity': request.POST.get('bulletin_board_quantity', 0),
            'scaffolding_quantity': request.POST.get('scaffolding_quantity', 0),
            'flag_quantity': request.POST.get('flag_quantity', 0),
            'philippine_flag_quantity': request.POST.get('philippine_flag_quantity', 0),
            'xu_flag_quantity': request.POST.get('xu_flag_quantity', 0),
            'ceiling_fans_quantity': request.POST.get('ceiling_fans_quantity', 0),
            'stand_fans_quantity': request.POST.get('stand_fans_quantity', 0),
            'iwata_fans_quantity': request.POST.get('iwata_fans_quantity', 0),
            'stage_non_acrylic_quantity': request.POST.get('stage_non_acrylic_quantity', 0),
            'digital_clock_quantity': request.POST.get('digital_clock_quantity', 0),
            'others_specify': request.POST.get('others_specify', ''),
            
            # Add quantities for manpower
            'security_quantity': request.POST.get('security_quantity', 0),
            'janitor_quantity': request.POST.get('janitor_quantity', 0),
            'electrician_quantity': request.POST.get('electrician_quantity', 0),
            'technician_quantity': request.POST.get('technician_quantity', 0),
            'assistant_technician_quantity': request.POST.get('assistant_technician_quantity', 0),
            'digital_clock_operator_quantity': request.POST.get('digital_clock_operator_quantity', 0),
            'plumber_quantity': request.POST.get('plumber_quantity', 0),
            'other_manpower_quantity': request.POST.get('other_manpower_quantity', 0),
        }

        # Get and validate date/time
        try:
            reservation_date = datetime.strptime(request.POST.get('date'), '%Y-%m-%d').date()
            start_time = datetime.strptime(request.POST.get('start_time'), '%H:%M').time()
            end_time = datetime.strptime(request.POST.get('end_time'), '%H:%M').time()

            if reservation_date < today:
                messages.error(request, 'Cannot make reservations for past dates')
                return render(request, 'user_portal/user_makereservation.html', {'form_data': form_data})

            if start_time >= end_time:
                messages.error(request, 'End time must be after start time')
                return render(request, 'user_portal/user_makereservation.html', {'form_data': form_data})

        except (ValueError, TypeError):
            messages.error(request, 'Invalid date or time format')
            return render(request, 'user_portal/user_makereservation.html', {'form_data': form_data})

        # Process facility and manpower requirements
        facility_keys = [
            'long_tables', 'mono_block_chairs', 'narra_chairs', 'podium', 'xu_seal',
            'xu_logo', 'sound_system', 'bulletin_board', 'scaffolding', 'flag', 'philippine_flag', 'xu_flag',
            'ceiling_fans', 'stand_fans', 'iwata_fans', 'stage_non_acrylic', 'digital_clock',
            'others'
        ]
        facilities_needed = {
            key.replace('_', ' ').title(): int(request.POST.get(f"{key}_quantity", 0)) 
            for key in facility_keys 
            if request.POST.get(f"{key}_quantity")
        }
        form_data['facilities_needed'] = facilities_needed

        manpower_keys = [
            'security', 'janitor', 'electrician', 'technician',
            'assistant_technician', 'digital_clock_operator', 'plumber', 'other_manpower'
        ]
        manpower_needed = {
            key.replace('_', ' ').title(): int(request.POST.get(f"{key}_quantity", 0)) 
            for key in manpower_keys 
            if request.POST.get(f"{key}_quantity")
        }
        form_data['manpower_needed'] = manpower_needed

        # Check time slot availability
        is_available, error_message = is_time_slot_available(reservation_date, start_time, end_time, form_data['facility'])
        if not is_available:
            messages.warning(request, f'Scheduling Conflict: {error_message}')
            # Create a notification about the blocked time slot
            Notification.objects.create(
                user=request.user,
                message=f"Your reservation attempt for {form_data['facility']} on {reservation_date.strftime('%B %d, %Y')} from {start_time.strftime('%I:%M %p')} to {end_time.strftime('%I:%M %p')} was blocked due to a scheduling conflict. Please select a different date or time.",
                notification_type='reservation_blocked'
            )
            return render(request, 'user_portal/user_makereservation.html', {'form_data': form_data})

        try:
            # Create the reservation
            reservation = Reservation.objects.create(
                user=request.user,
                organization=form_data['organization'],
                representative=form_data['representative'],
                contact_number=form_data['contact_number'],
                date_reserved=form_data['date_reserved'],
                date=reservation_date,
                insider_count=form_data['insider_count'],
                outsider_count=form_data['outsider_count'],
                start_time=start_time,
                end_time=end_time,
                reasons=form_data['reasons'],
                facility=form_data['facility'],
                facility_use=", ".join(form_data['facility_use']),
                event_type=", ".join(form_data['event_type']),
                facilities_needed=facilities_needed,
                manpower_needed=manpower_needed,
                status="Pending",
            )
            
            messages.success(request, 'Reservation created successfully! Your request will be reviewed by administrators.')
            return redirect('user_portal:user_myreservation')

        except Exception as e:
            messages.error(request, f'Error creating reservation: {str(e)}')
            return render(request, 'user_portal/user_makereservation.html', {'form_data': form_data})

    return render(request, 'user_portal/user_makereservation.html')


@login_required
def edit_reservation(request, id):
    reservation = get_object_or_404(Reservation, pk=id)
    
    # Prevent editing if reservation is completed
    if reservation.status == 'Completed':
        messages.error(request, "Cannot edit a completed reservation.")
        return redirect('user_portal:user_myreservation')

    if request.method == 'POST':
        try:
            # Get and validate date
            new_date = datetime.strptime(request.POST.get('date'), '%Y-%m-%d').date()
            if new_date < timezone.now().date():
                messages.error(request, 'Cannot set reservation date to a past date')
                return redirect('user_portal:edit_reservation', id=id)

            # Get and validate times
            start_time = datetime.strptime(request.POST.get('start_time'), '%H:%M').time()
            end_time = datetime.strptime(request.POST.get('end_time'), '%H:%M').time()
            
            if start_time >= end_time:
                messages.error(request, 'End time must be after start time')
                return redirect('user_portal:edit_reservation', id=id)

            # Check time slot availability, excluding current reservation
            other_reservations = Reservation.objects.filter(
                date=new_date,
                facility=reservation.facility,
                status__in=['Admin Approved', 'Billing Uploaded', 'Payment Pending', 'Payment Approved', 'Security Pass Issued', 'Completed']
            ).exclude(id=reservation.id)

            for other_res in other_reservations:
                if (start_time < other_res.end_time and end_time > other_res.start_time):
                    formatted_time = f"{other_res.start_time.strftime('%I:%M %p')} - {other_res.end_time.strftime('%I:%M %p')}"
                    messages.error(request, f"This facility is already reserved for {formatted_time} on {new_date.strftime('%B %d, %Y')}. Please choose a different time slot.")
                    return redirect('user_portal:edit_reservation', id=id)

            # Update reservation fields
            reservation.date = new_date
            reservation.start_time = start_time
            reservation.end_time = end_time

            # Update facilities to be used
            facilities = request.POST.getlist('facility_use')
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
                'other': request.POST.get('other_manpower_specifics', ''),
            }

            # Reset status to pending if significant fields were changed
            if (reservation.date != reservation.date or 
                reservation.start_time != reservation.start_time or 
                reservation.end_time != reservation.end_time):
                reservation.status = 'Pending'
                reservation.admin_approvals = {}
                messages.info(request, 'Your reservation has been updated and will need to be re-approved due to schedule changes.')

            reservation.save()
            messages.success(request, 'Reservation updated successfully!')
            return redirect('user_portal:user_myreservation')

        except ValueError as e:
            messages.error(request, f'Invalid input: {str(e)}')
            return redirect('user_portal:edit_reservation', id=id)
        except Exception as e:
            messages.error(request, f'Error updating reservation: {str(e)}')
            return redirect('user_portal:edit_reservation', id=id)

    # Prepopulate facility_use as list
    facilities_list = reservation.facility_use.split(', ') if reservation.facility_use else []

    # Prepare facilities_quantity and manpower_quantity dictionaries
    facilities_quantity = reservation.facilities_needed if reservation.facilities_needed else {}
    manpower_quantity = reservation.manpower_needed if reservation.manpower_needed else {}

    return render(request, 'user_portal/edit_reservation.html', {
        'reservation': reservation,
        'facilities_list': facilities_list,
        'facilities_quantity': facilities_quantity,
        'manpower_quantity': manpower_quantity,
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
    user_reservations = Reservation.objects.filter(user=request.user).order_by('-date')
    
    # Group reservations by status
    pending_reservations = user_reservations.filter(status__in=['Pending', 'Admin Approved', 'Billing Uploaded', 'Payment Pending', 'Payment Approved', 'Security Pass Issued'])
    approved_reservations = user_reservations.filter(status='Completed')  # Only completed reservations with confirmed security pass
    rejected = user_reservations.filter(status='Rejected')
    
    # Add formatted time to each reservation
    for reservation in user_reservations:
        reservation.formatted_time = f"{reservation.start_time.strftime('%I:%M %p')} - {reservation.end_time.strftime('%I:%M %p')}"
    
    # Get welcome message from session if it exists
    welcome_message = request.session.pop('welcome_message', None)
    if welcome_message:
        messages.success(request, welcome_message)
    
    context = {
        'pending_reservations': pending_reservations,
        'approved_reservations': approved_reservations,
        'rejected': rejected,
        'all_reservations': user_reservations,
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
                'formatted_time': f"{reservation.start_time.strftime('%I:%M %p')} - {reservation.end_time.strftime('%I:%M %p')}"
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
    # Only get completed reservations for the calendar
    reservations = Reservation.objects.filter(status='Completed')
    
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
            'status': r.status,
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

@login_required
def upload_receipt(request, reservation_id):
    """Upload payment receipt for a reservation"""
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    
    # Prevent uploading if reservation is completed
    if reservation.status == 'Completed':
        messages.error(request, "Cannot upload payment receipt for a completed reservation.")
        return redirect('user_portal:user_myreservation')
    
    # Check if reservation is in the correct state for payment
    if reservation.status != 'Billing Uploaded':
        messages.error(request, "Cannot upload payment receipt. Billing statement must be uploaded first.")
        return redirect('user_portal:user_myreservation')
    
    if request.method == 'POST':
        receipt_file = request.FILES.get('payment_receipt')
        
        if receipt_file:
            reservation.payment_receipt = receipt_file
            reservation.status = 'Payment Pending'  # Ensure status is updated correctly
            reservation.save()

            # Save the receipt file in the appropriate directory
            receipt_file_path = os.path.join(settings.MEDIA_ROOT, 'receipts', receipt_file.name)
            with open(receipt_file_path, 'wb+') as destination:
                for chunk in receipt_file.chunks():
                    destination.write(chunk)
            
            # Create notification for superuser about payment upload
            Notification.objects.create(
                user=User.objects.filter(is_superuser=True).first(),  # Notify the first superuser
                message=f"A payment receipt has been uploaded for reservation {reservation.id} at {reservation.facility_use} on {reservation.date}. Please verify the payment.",
                notification_type='payment_uploaded'
            )
            
            messages.success(request, "Payment receipt uploaded successfully. It will be reviewed shortly.")
        else:
            messages.error(request, "No file was uploaded. Please try again.")
    
    return redirect('user_portal:user_myreservation')

@login_required
def my_reservations(request):
    """View all user reservations"""
    reservations = Reservation.objects.filter(user=request.user).order_by('-date')
    
    # Process each reservation to show appropriate status and approval details
    for reservation in reservations:
        reservation.display_status = reservation.approval_status
        reservation.approval_details = reservation.admin_approval_details
        reservation.formatted_time = f"{reservation.start_time.strftime('%I:%M %p')} - {reservation.end_time.strftime('%I:%M %p')}"
    
    return render(request, 'user_portal/user_myreservation.html', {
        'reservations': reservations
    })

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from reservations.models import Reservation
from django.views.decorators.http import require_POST

@login_required
@require_POST
def upload_payment_receipt(request, reservation_id):
    """
    Handle the upload of payment receipt by the user
    """
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    if 'payment_receipt' not in request.FILES:
        messages.error(request, "No file was uploaded. Please select a file.")
        return redirect('user_portal:my_reservations')

    try:
        receipt_file = request.FILES['payment_receipt']
        file_extension = receipt_file.name.split('.')[-1].lower()
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'pdf']

        if file_extension not in allowed_extensions:
            messages.error(request, "Invalid file type. Please upload an image or PDF file.")
            return redirect('user_portal:my_reservations')

        reservation.payment_receipt = receipt_file
        reservation.status = 'Payment Uploaded'
        reservation.save()

        messages.success(request, "Payment receipt uploaded successfully! It will be reviewed shortly.")
        return redirect('user_portal:my_reservations')

    except Exception as e:
        messages.error(request, f"Error uploading payment receipt: {str(e)}")
        return redirect('user_portal:my_reservations')

@login_required
def dashboard(request):
    """
    Render the user dashboard.
    """
    return render(request, 'user_portal/dashboard.html')

@login_required
def profile(request):
    """
    Render the user profile page.
    """
    return render(request, 'user_portal/profile.html')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from reservations.models import Reservation
from .forms import ReservationForm

@login_required
def make_reservation(request):
    """
    Render the user make reservation page.
    """
    return render(request, 'user_portal/user_makereservation.html')

@login_required
def upload_security_pass(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    
    # Prevent uploading if reservation is completed
    if reservation.status == 'Completed':
        messages.error(request, "Cannot upload security pass for a completed reservation.")
        return redirect('user_portal:user_myreservation')
        
    if reservation.status != 'Security Pass Issued':
        messages.error(request, "Cannot upload security pass. Security pass must be issued by the superuser first.")
        return redirect('user_portal:user_myreservation')
    if request.method == 'POST':
        pass_file = request.FILES.get('security_pass_returned')
        if pass_file:
            reservation.security_pass_returned = pass_file
            reservation.security_pass_status = 'Pending'
            reservation.save()
            
            # Create notification for superuser about security pass upload
            Notification.objects.create(
                user=User.objects.filter(is_superuser=True).first(),
                message=f"A security pass has been uploaded for reservation {reservation.id} at {reservation.facility_use} on {reservation.date}. Please verify the security pass.",
                notification_type='security_pass_uploaded'
            )
            
            messages.success(request, "Security pass uploaded successfully. Awaiting confirmation.")
        else:
            messages.error(request, "No file was uploaded. Please try again.")
    return redirect('user_portal:user_myreservation')

def is_time_slot_available(date, start_time, end_time, facility):
    """
    Check if a time slot is available for a given facility
    Returns (bool, str): (is_available, error_message)
    """
    # Convert string times to datetime.time objects if they're strings
    if isinstance(start_time, str):
        start_time = datetime.strptime(start_time, '%H:%M').time()
    if isinstance(end_time, str):
        end_time = datetime.strptime(end_time, '%H:%M').time()

    # Check for existing approved reservations
    existing_reservations = Reservation.objects.filter(
        date=date,
        facility=facility,
        status__in=['Admin Approved', 'Billing Uploaded', 'Payment Pending', 'Payment Approved', 'Security Pass Issued', 'Completed']
    )

    for reservation in existing_reservations:
        # Check if there's any overlap in time
        if (start_time < reservation.end_time and end_time > reservation.start_time):
            formatted_time = f"{reservation.start_time.strftime('%I:%M %p')} - {reservation.end_time.strftime('%I:%M %p')}"
            return False, f"This facility is already reserved for {formatted_time} on {date.strftime('%B %d, %Y')}. Please choose a different time slot."

    # Validate business hours (assuming 6 AM to 10 PM)
    opening_time = time(6, 0)  # 6:00 AM
    closing_time = time(22, 0)  # 10:00 PM
    
    if start_time < opening_time or end_time > closing_time:
        return False, "Reservations must be between 6:00 AM and 10:00 PM"

    # Validate duration (maximum 8 hours)
    start_dt = datetime.combine(date, start_time)
    end_dt = datetime.combine(date, end_time)
    duration = end_dt - start_dt
    
    if duration.total_seconds() > 8 * 3600:  # 8 hours in seconds
        return False, "Reservations cannot exceed 8 hours"

    return True, ""