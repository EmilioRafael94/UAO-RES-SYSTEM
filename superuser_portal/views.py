from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import JsonResponse
from reservations.models import Reservation
from .models import Facility, TimeSlotTemplate, TimeSlot, BlockedDate
from datetime import timedelta, datetime
import json
from django.utils.crypto import get_random_string
import logging
from decimal import Decimal, InvalidOperation
import traceback
from user_portal.models import Notification
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from reservations.email_utils import send_reservation_email

def is_superuser(user):
    return user.is_superuser

@login_required
@user_passes_test(is_superuser)
def superuser_dashboard(request):
    # Get counts for KPIs
    unverified_payments = Reservation.objects.filter(payment_receipt__isnull=True).count()
    pending_passes = Reservation.objects.filter(security_pass__isnull=True).count()
    todays_reservations = Reservation.objects.filter(date=timezone.now().date()).count()
    active_users = User.objects.filter(is_active=True).count()
    
    # Get recent activity
    recent_activities = []
    recent_reservations = Reservation.objects.all().order_by('-updated_at')[:5]
    for res in recent_reservations:
        recent_activities.append({
            'timestamp': res.updated_at,
            'description': f"Reservation {res.id} status updated to {res.status}"
        })

    context = {
        'unverified_payments_count': unverified_payments,
        'pending_passes_count': pending_passes,
        'todays_reservations_count': todays_reservations,
        'active_users_count': active_users,
        'recent_activities': recent_activities
    }
    
    return render(request, 'superuser_portal/superuser_dashboard.html', context)

@login_required
@user_passes_test(is_superuser)
def manage_reservations(request):
    filter_type = request.GET.get('filter', 'all')

    # Filter reservations based on the selected filter type
    if filter_type == 'needs_billing':
        reservations = Reservation.objects.filter(
            status='Admin Approved'  # Only show reservations that have been approved by 4 admins
        )

    elif filter_type == 'needs_payment':
        reservations = Reservation.objects.filter(
            status='Billing Uploaded',
            payment_receipt__isnull=True
        )

    elif filter_type == 'needs_pass':
        reservations = Reservation.objects.filter(
            status='Payment Approved',
            security_pass__isnull=True
        )

    elif filter_type == 'today':
        reservations = Reservation.objects.filter(
            date_reserved=timezone.localdate()
        )

    elif filter_type == 'rejected':
        reservations = Reservation.objects.filter(status='Rejected')

    elif filter_type == 'completed':
        reservations = Reservation.objects.filter(status='Completed')

    else:  # 'all' or unknown filter
        reservations = Reservation.objects.all()

    # Process reservations for display
    reservations_data = []
    for res in reservations:
        # Determine the display status and admin approval count
        if res.status == 'Rejected':
            status = 'Rejected by admin(s)'
        elif res.status == 'Pending' or (len(res.admin_approvals or {}) < 4):
            status = 'Waiting for admin approval'
        elif len(res.admin_approvals or {}) >= 4 and res.status == 'Admin Approved':
            status = 'Approved by 4 admins. Billing and security pass process ready.'
        elif res.status == 'Completed':
            status = 'Completed'
        elif res.status == 'Billing Uploaded':
            status = 'Billing Uploaded'
        elif res.status == 'Payment Approved':
            status = 'Payment Approved'
        elif res.status == 'Security Pass Issued':
            status = 'Security Pass Issued'
        else:
            status = res.status

        reservations_data.append({
            'id': res.id,
            'reference': f'RES-{res.id:06d}',
            'facility': res.facility_use,
            'date': res.date,
            'status': status,
            'has_billing': bool(res.billing_statement),
            'has_payment': bool(res.payment_receipt),
            'has_pass': bool(res.security_pass),
            'receipt_file': res.payment_receipt,
            'admin_approvals': res.admin_approvals,
            'admin_rejections': res.admin_rejections,
            'security_pass_status': res.security_pass_status,
            'admin_approval_count': len(res.admin_approvals or {}),
        })

    context = {
        'reservations': reservations_data,
        'current_filter': filter_type
    }
    return render(request, 'superuser_portal/superuser_managereservations.html', context)

@login_required
@user_passes_test(is_superuser)
def verify_payment(request, reservation_id):
    """
    Handle payment verification or rejection by superuser
    """
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    try:
        # Parse the JSON data from request body
        data = json.loads(request.body)
        action = data.get('action')

        reservation = get_object_or_404(Reservation, id=reservation_id)

        if action == 'verify':
            # Update reservation status
            reservation.status = 'Payment Approved'  # Use 'Payment Approved' for consistency
            reservation.payment_verified = True
            reservation.payment_verified_by = request.user
            reservation.payment_verified_date = timezone.now()
            reservation.payment_rejection_reason = ''  # Clear any previous rejection reason
            reservation.save()
            # Do NOT send security pass email here
            return JsonResponse({
                'success': True,
                'message': 'Payment verified successfully'
            })

        elif action == 'reject':
            reason = data.get('reason', 'No reason provided')

            # Update reservation status
            reservation.status = 'Payment Rejected'
            reservation.payment_rejection_reason = reason
            reservation.payment_verified = False
            reservation.payment_verified_by = None
            reservation.payment_verified_date = None
            reservation.save()

            return JsonResponse({
                'success': True,
                'message': 'Payment rejection processed',
                'rejection_reason': reason
            })

        else:
            return JsonResponse({'success': False, 'error': 'Invalid action'}, status=400)

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@user_passes_test(is_superuser)
def verify_pass(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    if request.method == 'POST':
        # Handle security pass verification logic
        reservation.pass_verified = True
        reservation.save()
        return redirect('superuser_portal:manage_reservations')
    return render(request, 'superuser/verify_pass.html', {'reservation': reservation})

@login_required
@user_passes_test(is_superuser)
def system_settings(request):
    facilities = Facility.objects.all().order_by('name')
    blocked_dates = BlockedDate.objects.all().select_related('facility')
    
    context = {
        'facilities': facilities,
        'blocked_dates': blocked_dates
    }
    
    return render(request, 'superuser_portal/superuser_systemsettings.html', context)

@login_required
@user_passes_test(is_superuser)
def manage_facility(request, facility_id=None):
    if request.method == 'POST':
        if facility_id:
            facility = get_object_or_404(Facility, id=facility_id)
        else:
            facility = Facility()
        
        facility.name = request.POST.get('name')
        facility.capacity = request.POST.get('capacity')
        facility.description = request.POST.get('description')
        facility.save()
        
        return redirect('superuser_portal:system_settings')
    
    if facility_id:
        facility = get_object_or_404(Facility, id=facility_id)
        return JsonResponse({
            'id': facility.id,
            'name': facility.name,
            'capacity': facility.capacity,
            'description': facility.description
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
@user_passes_test(is_superuser)
def delete_facility(request, facility_id):
    if request.method == 'POST':
        facility = get_object_or_404(Facility, id=facility_id)
        facility.delete()
        return JsonResponse({'status': 'success', 'message': 'Facility deleted successfully.'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
@user_passes_test(is_superuser)
def manage_time_template(request, template_id=None):
    if request.method == 'POST':
        if template_id:
            template = get_object_or_404(TimeSlotTemplate, id=template_id)
            # Delete existing slots
            template.slots.all().delete()
        else:
            template = TimeSlotTemplate()
        
        template.name = request.POST.get('name')
        template.save()
        
        # Add new time slots
        start_times = request.POST.getlist('start_time[]')
        end_times = request.POST.getlist('end_time[]')
        
        for start, end in zip(start_times, end_times):
            TimeSlot.objects.create(
                template=template,
                start_time=start,
                end_time=end
            )
        
        return redirect('superuser_portal:system_settings')
    
    if template_id:
        template = get_object_or_404(TimeSlotTemplate, id=template_id)
        return JsonResponse({
            'id': template.id,
            'name': template.name,
            'slots': [{'start': slot.start_time.strftime('%H:%M'),
                      'end': slot.end_time.strftime('%H:%M')} 
                     for slot in template.slots.all()]
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
@user_passes_test(is_superuser)
def delete_time_template(request, template_id):
    if request.method == 'POST':
        template = get_object_or_404(TimeSlotTemplate, id=template_id)
        template.delete()
        return JsonResponse({'status': 'success', 'message': 'Time template deleted successfully.'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
@user_passes_test(is_superuser)
def manage_blocked_dates(request):
    if request.method == 'POST':
        facility_id = request.POST.get('facility')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        reason = request.POST.get('reason')
        
        BlockedDate.objects.create(
            facility_id=facility_id,
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time,
            reason=reason,
            created_by=request.user
        )
        
        return redirect('superuser_portal:system_settings')
    
    blocked_dates = BlockedDate.objects.all().select_related('facility')
    return JsonResponse({
        'blocked_dates': [{'facility': bd.facility.name,
                          'start': bd.start_date.isoformat(),
                          'end': bd.end_date.isoformat(),
                          'reason': bd.reason}
                         for bd in blocked_dates]
    })

@login_required
@user_passes_test(is_superuser)
def delete_blocked_date(request, date_id):
    if request.method == 'POST':
        blocked_date = get_object_or_404(BlockedDate, id=date_id)
        blocked_date.delete()
        return JsonResponse({'status': 'success', 'message': 'Blocked date deleted successfully.'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
@user_passes_test(is_superuser)
def user_roles(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'superuser_portal/superuser_userroles.html', {'users': users})

@login_required
@user_passes_test(is_superuser)
def change_user_role(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        new_role = request.POST.get('role')
        
        # Reset all role flags first
        user.is_staff = False
        user.is_superuser = False
        
        # Set appropriate role
        if new_role == 'superuser':
            user.is_superuser = True
        elif new_role == 'admin':
            user.is_staff = True
        # Regular users have no special permissions
        
        user.save()
        return redirect('superuser_portal:user_roles')
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
@user_passes_test(is_superuser)
def reset_user_password(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        # Generate a random password with 12 characters
        new_password = get_random_string(length=12)
        user.set_password(new_password)
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Password has been reset',
            'new_password': new_password  # In production, send via email instead
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
@user_passes_test(is_superuser)
def update_user_status(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        data = json.loads(request.body)
        active = data.get('active', False)
        
        user.is_active = active
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': f'User {"activated" if active else "deactivated"} successfully'
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
@user_passes_test(is_superuser)
def superuser_profile(request):
    return render(request, 'superuser_portal/superuser_profile.html')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
@user_passes_test(is_superuser)
@csrf_exempt  # Only if you handle CSRF manually in JS
def upload_billing(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    if request.method == 'POST':
        billing_file = request.FILES.get('billing_file')
        amount = request.POST.get('amount')
        due_date = request.POST.get('due_date')

        if billing_file and amount and due_date:
            reservation.billing_statement = billing_file
            reservation.amount = amount
            reservation.due_date = due_date
            reservation.status = 'Billing Issued'  # Ensure status is updated correctly
            reservation.save()
            if request.user.is_authenticated:
                messages.success(request, 'Billing uploaded successfully.')
        else:
            if request.user.is_authenticated:
                messages.error(request, 'All fields are required to upload billing.')

        return redirect('superuser_portal:superuser_dashboard')

    return render(request, 'superuser/upload_billing.html', {'reservation': reservation})

@login_required
@user_passes_test(is_superuser)
@require_GET
def reservation_details(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    # Billing info
    billing = {
        'statement_url': reservation.billing_statement.url if reservation.billing_statement else None,
        'can_upload': reservation.status == 'Admin Approved',
        'amount': str(reservation.amount) if hasattr(reservation, 'amount') and reservation.amount else None,
        'due_date': reservation.due_date.strftime('%Y-%m-%d') if hasattr(reservation, 'due_date') and reservation.due_date else None,
    }
    # Payment info
    payment = {
        'receipt_url': reservation.payment_receipt.url if reservation.payment_receipt else None,
        'can_verify': reservation.status == 'Payment Pending',
        'id': reservation.id,
        'status': reservation.status,
        'rejection_reason': reservation.payment_rejection_reason or '',
    }
    # Security pass info
    can_upload_pass = reservation.status in ['Payment Approved', 'Needs Security Pass', 'Security Pass Needed'] and not reservation.security_pass
    pass_info = {
        'file_url': reservation.security_pass.url if reservation.security_pass else None,
        'returned_url': reservation.security_pass_returned.url if reservation.security_pass_returned else None,
        'can_upload': can_upload_pass,
        'id': reservation.id,
        'status': reservation.security_pass_status,
        'rejection_reason': reservation.security_pass_rejection_reason or '',
    }
    return JsonResponse({
        'billing': billing,
        'payment': payment,
        'pass': pass_info,
        'status': reservation.status,
    })

@login_required
@user_passes_test(is_superuser)
@csrf_exempt  # Only if you handle CSRF manually in JS
def upload_billing_statement(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    if request.method == 'POST' and request.FILES.get('billing_statement'):
        reservation.billing_statement = request.FILES['billing_statement']
        reservation.status = 'Billing Uploaded'
        reservation.save()
        
        # Create notification for user about billing statement
        Notification.objects.create(
            user=reservation.user,
            message=f"A billing statement has been uploaded for your reservation at {reservation.facility_use} on {reservation.date}. Please upload your payment receipt.",
            notification_type='billing_uploaded'
        )
        
        # Send email: Billing Form Available
        send_reservation_email(
            reservation.user,
            'Billing Form Available',
            'billing_form_available_email.html',
            {'subject': 'Billing Form Available', 'user': reservation.user, 'reservation': reservation}
        )
        
        return JsonResponse({'success': True, 'file_url': reservation.billing_statement.url})
    return JsonResponse({'success': False, 'error': 'Invalid request.'})

@login_required
@user_passes_test(is_superuser)
@require_GET
def get_reservation_details(request, reservation_id):
    """
    Returns detailed information about a reservation in JSON format
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    try:
        reservation = get_object_or_404(Reservation, id=reservation_id)

        # Prepare billing data
        billing_data = {
            'statement_url': reservation.billing_statement.url if reservation.billing_statement else None,
        }

        # Prepare payment data
        payment_data = {
            'id': reservation_id,  # Using reservation ID for payment operations
            'receipt_url': reservation.payment_receipt.url if reservation.payment_receipt else None,
            'verified': reservation.payment_verified,
            'rejected': True if reservation.status == 'Payment Rejected' else False,
            'rejection_reason': reservation.payment_rejection_reason if hasattr(reservation, 'payment_rejection_reason') else None
        }

        # Prepare security pass data (placeholder for now)
        pass_data = {
            'id': reservation_id,
            'file_url': reservation.security_pass.url if reservation.security_pass else None,
            'returned_url': reservation.security_pass_returned.url if reservation.security_pass_returned else None,
            'can_upload': reservation.status in ['Payment Approved', 'Needs Security Pass', 'Security Pass Needed'] and not reservation.security_pass,
            'status': reservation.security_pass_status,
            'rejection_reason': reservation.security_pass_rejection_reason or '',
        }

        return JsonResponse({
            'billing': billing_data,
            'payment': payment_data,
            'pass': pass_data,
            'status': reservation.status,
            'admin_approval_count': len(reservation.admin_approvals or {}),
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(is_superuser)
def upload_security_pass(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    if request.method == 'POST' and request.FILES.get('security_pass'):
        reservation.security_pass = request.FILES['security_pass']
        reservation.status = 'Security Pass Issued'
        reservation.security_pass_status = 'Pending'
        reservation.save()
        # Send email: Security Pass Released (moved here from payment verification)
        send_reservation_email(
            reservation.user,
            'Security Pass Form Released',
            'security_pass_released_email.html',
            {'subject': 'Security Pass Form Released', 'user': reservation.user, 'reservation': reservation}
        )
        return JsonResponse({'success': True, 'file_url': reservation.security_pass.url})
    elif request.method == 'POST':
        return JsonResponse({'success': False, 'error': 'No file uploaded.'})
    return JsonResponse({'success': False, 'error': 'Invalid request.'})

@login_required
@user_passes_test(is_superuser)
def confirm_security_pass(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    if request.method == 'POST':
        reservation.security_pass_status = 'Confirmed'
        reservation.status = 'Completed'
        reservation.save()
        
        # Create notification for user about completed reservation
        Notification.objects.create(
            user=reservation.user,
            message=f"Your reservation for {reservation.facility_use} on {reservation.date} has been completed. The security pass has been confirmed.",
            notification_type='reservation_completed'
        )
        
        # Send email: Reservation Confirmed
        send_reservation_email(
            reservation.user,
            'Reservation Confirmed',
            'reservation_confirmed_email.html',
            {'subject': 'Reservation Confirmed', 'user': reservation.user, 'reservation': reservation}
        )
        
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request.'})

@login_required
@user_passes_test(is_superuser)
def reject_security_pass(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        if not reason:
            return JsonResponse({'success': False, 'error': 'Rejection reason is required.'})
        reservation.security_pass_status = 'Rejected'
        reservation.security_pass_rejection_reason = reason
        reservation.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request.'})

