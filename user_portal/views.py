from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from user_portal.forms import UserUpdateForm, ProfileUpdateForm
from reservations.models import Reservation
from django.contrib import messages
from django.utils import timezone
import json
from django.http import JsonResponse
from .models import Notification
from django.contrib.auth.models import User
from django.conf import settings
import os
from django.core.mail import send_mail
import random
from django.core.cache import cache
from superuser_portal.models import BlockedDate, Facility
from django.db.models import Q


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
    sort = request.GET.get('sort', 'newest')
    if sort == 'oldest':
        reservations = Reservation.objects.filter(user=request.user).order_by('id')
    else:
        reservations = Reservation.objects.filter(user=request.user).order_by('-id')
    for reservation in reservations:
        if hasattr(reservation, 'reserved_dates') and reservation.reserved_dates:
            reservation.display_dates = reservation.reserved_dates
            reservation.display_dates_list = [d.strip() for d in reservation.reserved_dates.split(',') if d.strip()]
        else:
            reservation.display_dates = reservation.date
            reservation.display_dates_list = [str(reservation.date)]
        admin_approval_count = len(getattr(reservation, 'admin_approvals', {}) or {})
        admin_rejection_count = len(getattr(reservation, 'admin_rejections', {}) or {})
        # --- FIXED LOGIC FOR BILLING/SECURITY PASS STATUS ---
        if reservation.status == 'Rejected' or admin_rejection_count > 0:
            reservation.display_status = 'Rejected by admin(s)'
        elif reservation.status == 'Pending' and admin_approval_count < 4:
            reservation.display_status = f'Pending ({admin_approval_count}/4 admins approved)'
        elif admin_approval_count == 4 and reservation.status == 'Admin Approved':
            reservation.display_status = '4 admins approved, wait for billing'
        elif reservation.status == 'Billing Uploaded':
            reservation.display_status = 'Processing (billing uploaded, wait for payment)'
        elif reservation.status == 'Payment Pending':
            reservation.display_status = 'Processing (payment uploaded, wait for verification)'
        elif reservation.status == 'Payment Approved':
            reservation.display_status = 'Processing (payment verified, wait for security pass)'
        elif reservation.status == 'Security Pass Issued':
            # Show billing as approved and security pass as issued
            reservation.display_status = 'Billing approved, security pass issued, wait for completion'
        elif reservation.status == 'Completed':
            reservation.display_status = 'Completed'
        else:
            reservation.display_status = getattr(reservation, 'approval_status', reservation.status)
    return render(request, 'user_portal/user_myreservation.html', {'reservations': reservations})


@login_required
def user_makereservation(request):
    today = timezone.now().date()

    if request.method == 'POST':
        print("\n=== Form Submission Data ===")
        for key, value in request.POST.items():
            print(f"{key}: {value}")
        print("===========================\n")

        organization = request.POST.get('organization')
        representative = request.POST.get('representative')
        contact_number = request.POST.get('contact_number')
        dates = request.POST.get('dates')
        if dates:
            date_list = [d.strip() for d in dates.split(',') if d.strip()]
        else:
            date_list = []
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        date_reserved = request.POST.get('date_reserved')
        facilities = request.POST.getlist('facilities')
        event_types = request.POST.getlist('event_type')
        if not event_types:
            messages.error(request, 'Please select at least one event type')
            return redirect('user_portal:user_makereservation')
        event_type = ', '.join(event_types)

        facilities_needed = {
            'Long Tables': int(request.POST.get('long_tables_quantity') or 0),
            'Mono Block Chairs': int(request.POST.get('mono_block_chairs_quantity') or 0),
            'Narra Chairs': int(request.POST.get('narra_chairs_quantity') or 0),
            'Podium': int(request.POST.get('podium_quantity') or 0),
            'XU Seal': int(request.POST.get('xu_seal_quantity') or 0),
            'XU Logo': int(request.POST.get('xu_logo_quantity') or 0),
            'Sound System': int(request.POST.get('sound_system_quantity') or 0),
            'Bulletin Board': int(request.POST.get('bulletin_board_quantity') or 0),
            'Scaffolding': int(request.POST.get('scaffolding_quantity') or 0),
            'Flag': int(request.POST.get('flag_quantity') or 0),
            'Philippine Flag': int(request.POST.get('philippine_flag_quantity') or 0),
            'XU Flag': int(request.POST.get('xu_flag_quantity') or 0),
            'Ceiling Fans': int(request.POST.get('ceiling_fans_quantity') or 0),
            'Stand Fans': int(request.POST.get('stand_fans_quantity') or 0),
            'Iwata Fans': int(request.POST.get('iwata_fans_quantity') or 0),
            'Stage Non-Acrylic': int(request.POST.get('stage_non_acrylic_quantity') or 0),
            'Digital Clock': int(request.POST.get('digital_clock_quantity') or 0),
            'Others': request.POST.get('others_specify', ''),
        }
        manpower_needed = {
            'Security': int(request.POST.get('security_quantity') or 0),
            'Janitor': int(request.POST.get('janitor_quantity') or 0),
            'Electrician': int(request.POST.get('electrician_quantity') or 0),
            'Technician': int(request.POST.get('technician_quantity') or 0),
            'Assistant Technician': int(request.POST.get('assistant_technician_quantity') or 0),
            'Digital Clock Operator': int(request.POST.get('digital_clock_operator_quantity') or 0),
            'Plumber': int(request.POST.get('plumber_quantity') or 0),
            'Other': int(request.POST.get('other_manpower_quantity') or 0),
        }
        letter = request.FILES.get('letter')

        required_fields = [organization, representative, contact_number, date_list, start_time, end_time, facilities, event_types, letter]
        if not all(required_fields):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('user_portal:user_makereservation')
        blocked_found = False
        blocked_message = None
        for date in date_list:
            for facility_name in facilities:
                try:
                    facility_obj = Facility.objects.get(name=facility_name)
                except Facility.DoesNotExist:
                    messages.error(request, f"Facility '{facility_name}' does not exist.")
                    return redirect('user_portal:user_makereservation')
                blocked_qs = BlockedDate.objects.filter(
                    facility=facility_obj,
                    date=date
                ).filter(
                    Q(start_time__lt=end_time, end_time__gt=start_time)
                )
                if blocked_qs.exists():
                    blocked_found = True
                    blocked = blocked_qs.first()
                    blocked_message = f'The facility "{facility_name}" is not available on {date} from {blocked.start_time.strftime("%H:%M")} to {blocked.end_time.strftime("%I:%M%p")}. This time slot is blocked'
        if blocked_found:
            messages.error(request, blocked_message or 'Please review your reservation. One or more selected dates and facilities are blocked.')
            return redirect('user_portal:user_makereservation')
        for date in date_list:
            overlap = Reservation.objects.filter(
                facility__in=facilities,
                date=date,
                start_time__lt=end_time,
                end_time__gt=start_time,
            ).exclude(status__in=['Rejected', 'Cancelled']).exists()
            if overlap:
                messages.error(request, 'The selected facility, date, or time is already reserved. Please look at the calendar.')
                return redirect('user_portal:user_makereservation')
        try:
            reserved_dates_str = ', '.join(date_list)
            for date in date_list:
                reservation = Reservation.objects.create(
                    user=request.user,
                    organization=organization,
                    representative=representative,
                    contact_number=contact_number,
                    date=date,
                    date_reserved=date_reserved,
                    start_time=start_time,
                    end_time=end_time,
                    facility=", ".join(facilities),
                    facility_use=", ".join(facilities),
                    event_type=event_type,
                    insider_count=int(request.POST.get('insider_count') or 0),
                    outsider_count=int(request.POST.get('outsider_count') or 0),
                    facilities_needed=facilities_needed,
                    manpower_needed=manpower_needed,
                    status="Pending",
                    letter=letter if hasattr(Reservation, 'letter') else None,
                    reserved_dates=reserved_dates_str if hasattr(Reservation, 'reserved_dates') else None
                )
                if letter and hasattr(reservation, 'letter'):
                    reservation.letter = letter
                    reservation.save()
            messages.success(request, 'Reservation(s) created successfully!')
        except Exception as e:
            messages.error(request, f'Error creating reservation: {str(e)}')
            return redirect('user_portal:user_makereservation')
        return redirect('user_portal:user_myreservation')
    return render(request, 'user_portal/user_makereservation.html', {'today': today})



@login_required
def edit_reservation(request, id):
    reservation = get_object_or_404(Reservation, pk=id)
    
    if reservation.status == 'Completed':
        messages.error(request, "Cannot edit a completed reservation.")
        return redirect('user_portal:user_myreservation')

    if request.method == 'POST':
        reservation.date = request.POST.get('date')
        reservation.start_time = request.POST.get('start_time')
        reservation.end_time = request.POST.get('end_time')

        facilities = request.POST.getlist('facility_use')
        reservation.facility_use = ", ".join(facilities)

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

    facilities_list = reservation.facility_use.split(', ') if reservation.facility_use else []

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

@login_required
def user_dashboard(request):
    user_reservations = Reservation.objects.filter(user=request.user).order_by('-date')
    
    pending_reservations = user_reservations.filter(status__in=['Pending', 'Admin Approved', 'Billing Uploaded', 'Payment Pending', 'Payment Approved', 'Security Pass Issued'])
    approved_reservations = user_reservations.filter(status='Completed')
    rejected = user_reservations.filter(status='Rejected')
    
    for reservation in user_reservations:
        reservation.formatted_time = f"{reservation.start_time.strftime('%I:%M %p')} - {reservation.end_time.strftime('%I:%M %p')}"
    
    context = {
        'pending_reservations': pending_reservations,
        'approved_reservations': approved_reservations,
        'rejected': rejected,
        'all_reservations': user_reservations,
    }
    return render(request, 'user_portal/user_dashboard.html', context)

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
                profile_instance.course = ''

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
    reservations = Reservation.objects.filter(status='Completed')
    
    blocked_dates = BlockedDate.objects.all()
    
    events = []
    
    for r in reservations:
        facilities_list = []
        if isinstance(r.facilities_needed, dict):
            for facility, quantity in r.facilities_needed.items():
                facilities_list.append(f"{facility}: {quantity}")
        else:
            facilities_list.append('None')

        manpower_list = []
        if isinstance(r.manpower_needed, dict):
            for manpower, quantity in r.manpower_needed.items():
                manpower_list.append(f"{manpower}: {quantity}")
        else:
            manpower_list.append('None')

        events.append({
            'title': r.facility_use,
            'start': f"{r.date}T{r.start_time}",
            'end': f"{r.date}T{r.end_time}",
            'event_type': r.event_type,
            'facilities_needed': ', '.join(facilities_list) if facilities_list else 'None',
            'manpower_needed': ', '.join(manpower_list) if manpower_list else 'None',
            'status': r.status,
            'color': '#28a745'
        })
    
    for bd in blocked_dates:
        events.append({
            'title': f"{bd.facility.name} (Blocked)",
            'start': f"{bd.date}T{bd.start_time}",
            'end': f"{bd.date}T{bd.end_time}",
            'event_type': 'Blocked',
            'facilities_needed': bd.facility.name,
            'manpower_needed': 'None',
            'status': 'Blocked',
            'color': '#dc3545',
            'extendedProps': {
                'reason': bd.reason
            }
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
            return redirect('user_portal:user_profile')
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
    show_verification_modal = False
    code_error = None
    gmail_limit_reached = cache.get('gmail_smtp_limit_reached', False)

    if request.method == 'POST':
        if 'send_verification_code' in request.POST:
            if gmail_limit_reached:
                messages.error(request, 'Email sending limit for verification codes has been reached. Please try again tomorrow or contact support.')
            else:
                code = f"{random.randint(100000, 999999)}"
                profile = request.user.profile
                profile.verification_code = code
                profile.save()
                try:
                    send_mail(
                        'Your Email Verification Code',
                        f'Your verification code is: {code}',
                        settings.DEFAULT_FROM_EMAIL,
                        [request.user.email],
                        fail_silently=False,
                    )
                    show_verification_modal = True
                except Exception as e:
                    messages.error(request, 'Failed to send verification code. Please try again later.')
        elif 'verify_code' in request.POST:
            code = request.POST.get('verification_code')
            profile = request.user.profile
            if code == profile.verification_code:
                profile.is_verified = True
                profile.verification_code = None
                profile.save()
                messages.success(request, 'Your email has been verified!')
            else:
                show_verification_modal = True
                code_error = 'Invalid code. Please try again.'

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'show_verification_modal': show_verification_modal,
        'code_error': code_error,
        'gmail_limit_reached': gmail_limit_reached,
    }
    return render(request, 'user_portal/user_profile.html', context)

def send_notification(user, message):
    notification = Notification.objects.create(user=user, message=message)
    notification.save()

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

    send_notification(reservation.user, f"Your reservation for {reservation.facility} is now {status}.")

    return redirect('user_portal:user_myreservation')

@login_required
def upload_receipt(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    if reservation.status == 'Completed':
        messages.error(request, "Cannot upload payment receipt for a completed reservation.")
        return redirect('user_portal:user_myreservation')

    if reservation.status not in ['Billing Uploaded', 'Payment Rejected']:
        messages.error(request, "Cannot upload payment receipt. Billing statement must be uploaded first or previous payment must be rejected.")
        return redirect('user_portal:user_myreservation')

    if request.method == 'POST':
        receipt_file = request.FILES.get('payment_receipt')
        if receipt_file:
            reservation.payment_receipt = receipt_file
            reservation.status = 'Payment Pending'
            reservation.save()

            receipt_file_path = os.path.join(settings.MEDIA_ROOT, 'receipts', receipt_file.name)
            with open(receipt_file_path, 'wb+') as destination:
                for chunk in receipt_file.chunks():
                    destination.write(chunk)
            Notification.objects.create(
                user=User.objects.filter(is_superuser=True).first(),
                message=f"A payment receipt has been uploaded for reservation {reservation.id} at {reservation.facility_use} on {reservation.date}. Please verify the payment.",
                notification_type='payment_uploaded'
            )
            messages.success(request, "Payment receipt uploaded successfully. It will be reviewed shortly.")
        else:
            messages.error(request, "No file was uploaded. Please try again.")
    return redirect('user_portal:user_myreservation')

@login_required
def my_reservations(request):
    reservations = Reservation.objects.filter(user=request.user).order_by('-date')
    
    for reservation in reservations:
        if hasattr(reservation, 'reserved_dates') and reservation.reserved_dates:
            reservation.display_dates = reservation.reserved_dates
            reservation.display_dates_list = [d.strip() for d in reservation.reserved_dates.split(',') if d.strip()]
        else:
            reservation.display_dates = reservation.date
            reservation.display_dates_list = [str(reservation.date)]

        admin_approval_count = len(reservation.admin_approvals or {})
        admin_rejection_count = len(reservation.admin_rejections or {})
        reservation.can_edit = reservation.status not in ['Rejected', 'Completed']
        reservation.can_delete = True
        if reservation.status == 'Rejected' or admin_rejection_count > 0:
            reservation.display_status = 'Rejected by admin(s)'
            reservation.can_edit = False
        elif reservation.status == 'Pending' and admin_approval_count < 4:
            reservation.display_status = f'Pending ({admin_approval_count}/4 admins approved)'
        elif admin_approval_count == 4 and reservation.status == 'Admin Approved':
            reservation.display_status = '4 admins approved, wait for billing'
        elif reservation.status == 'Billing Uploaded':
            reservation.display_status = 'Processing (billing uploaded, wait for payment)'
        elif reservation.status == 'Payment Pending':
            reservation.display_status = 'Processing (payment uploaded, wait for verification)'
        elif reservation.status == 'Payment Approved':
            reservation.display_status = 'Processing (payment verified, wait for security pass)'
        elif reservation.status == 'Security Pass Issued':
            # Show billing as approved and security pass as issued
            reservation.display_status = 'Billing approved, security pass issued, wait for completion'
        elif reservation.status == 'Completed':
            reservation.display_status = 'Completed'
        else:
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
    if reservation.status == 'Completed':
        messages.error(request, "Cannot upload security pass for a completed reservation.")
        return redirect('user_portal:user_myreservation')
    if reservation.status != 'Security Pass Issued' and reservation.security_pass_status != 'Rejected':
        messages.error(request, "Cannot upload security pass. Security pass must be issued by the superuser first or previous pass must be rejected.")
        return redirect('user_portal:user_myreservation')
    if request.method == 'POST':
        pass_file = request.FILES.get('security_pass_returned')
        if pass_file:
            reservation.security_pass_returned = pass_file
            reservation.security_pass_status = 'Pending'
            reservation.save()
            Notification.objects.create(
                user=User.objects.filter(is_superuser=True).first(),
                message=f"A security pass has been uploaded for reservation {reservation.id} at {reservation.facility_use} on {reservation.date}. Please verify the security pass.",
                notification_type='security_pass_uploaded'
            )
            messages.success(request, "Security pass uploaded successfully. Awaiting confirmation.")
        else:
            messages.error(request, "No file was uploaded. Please try again.")
    return redirect('user_portal:user_myreservation')

@login_required
def check_date_availability(request):
    """AJAX endpoint to check if a date is available for reservation"""
    date = request.GET.get('date')
    facility = request.GET.get('facility')
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')
    
    if not all([date, facility, start_time, end_time]):
        return JsonResponse({
            'available': False,
            'error': 'Missing required parameters'
        })
    
    blocked = BlockedDate.objects.filter(
        facility__name=facility,
        date=date,
        start_time__lt=end_time,
        end_time__gt=start_time
    ).first()
    
    if blocked:
        return JsonResponse({
            'available': False,
            'error': 'This time slot is blocked',
            'blocked_start_time': blocked.start_time.strftime('%I:%M %p'),
            'blocked_end_time': blocked.end_time.strftime('%I:%M %p'),
            'blocked_date': blocked.date.strftime('%Y-%m-%d'),
            'blocked_facility': blocked.facility.name,
        })
    
    overlap = Reservation.objects.filter(
        facility__icontains=facility,
        date=date,
        start_time__lt=end_time,
        end_time__gt=start_time,
    ).exclude(status__in=['Rejected', 'Cancelled']).exists()
    
    return JsonResponse({
        'available': not overlap
    })