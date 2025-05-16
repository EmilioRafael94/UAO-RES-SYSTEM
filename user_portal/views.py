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
    user_reservations = Reservation.objects.filter(user=request.user).order_by('-date')
    
    # Group reservations by status
    pending_reservations = user_reservations.filter(status='Pending')
    approved_reservations = user_reservations.filter(status='Admin Approved')
    billing_uploaded = user_reservations.filter(status='Billing Uploaded')
    payment_pending = user_reservations.filter(status='Payment Pending')
    payment_approved = user_reservations.filter(status='Payment Approved')
    security_pass = user_reservations.filter(status='Security Pass Issued')
    completed = user_reservations.filter(status='Completed')
    rejected = user_reservations.filter(status='Rejected')
    
    # Add formatted time to each reservation
    for reservation in user_reservations:
        reservation.formatted_time = f"{reservation.start_time.strftime('%I:%M %p')} - {reservation.end_time.strftime('%I:%M %p')}"
    
    context = {
        'pending_reservations': pending_reservations,
        'approved_reservations': approved_reservations,
        'billing_uploaded': billing_uploaded,
        'payment_pending': payment_pending,
        'payment_approved': payment_approved,
        'security_pass': security_pass,
        'completed': completed,
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

@login_required
def upload_receipt(request, reservation_id):
    """Upload payment receipt for a reservation"""
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    
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
    if reservation.status != 'Security Pass Issued':
        messages.error(request, "Cannot upload security pass. Security pass must be issued by the superuser first.")
        return redirect('user_portal:user_myreservation')
    if request.method == 'POST':
        pass_file = request.FILES.get('security_pass_returned')
        if pass_file:
            reservation.security_pass_returned = pass_file
            reservation.security_pass_status = 'Pending'
            reservation.save()
            messages.success(request, "Security pass uploaded successfully. Awaiting confirmation.")
        else:
            messages.error(request, "No file was uploaded. Please try again.")
    return redirect('user_portal:user_myreservation')