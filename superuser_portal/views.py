import decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import JsonResponse
from .models import Facility, TimeSlotTemplate, TimeSlot, BlockedDate
from datetime import timedelta
import json
from django.utils.crypto import get_random_string
from user_portal.models import Reservation
from django.http import JsonResponse, Http404
from .forms import BillingForm, SecurityPassForm
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import logging
import traceback
from decimal import Decimal, InvalidOperation
from datetime import datetime


def is_superuser(user):
    return user.is_superuser

@login_required
@user_passes_test(is_superuser)
def superuser_dashboard(request):
    today = timezone.localdate()

    unverified_payments = Reservation.objects.filter(receipt_file__isnull=True).count()
    pending_passes = Reservation.objects.filter(security_pass_pdf__isnull=True).count()
    todays_reservations = Reservation.objects.filter(date_reserved=today).count()
    active_users = User.objects.filter(is_active=True).count()

    recent_activities = []
    recent_reservations = Reservation.objects.order_by('-updated_at')[:5]
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
    return render(request, 'superuser/superuser_dashboard.html', context)

@login_required
@user_passes_test(is_superuser)
def manage_reservations(request):
    filter_type = request.GET.get('filter', 'all')

    # Filter reservations based on the selected filter type
    if filter_type == 'needs_billing':
        reservations = Reservation.objects.filter(
            billing_file__isnull=True
        ).exclude(status='Rejected')

    elif filter_type == 'needs_payment':
        reservations = Reservation.objects.filter(
            billing_file__isnull=False,
            receipt_file__isnull=True
        ).exclude(status='Rejected')

    elif filter_type == 'needs_pass':
        reservations = Reservation.objects.filter(
            receipt_file__isnull=False,
            security_pass_pdf__isnull=True
        ).exclude(status='Rejected')

    elif filter_type == 'today':
        reservations = Reservation.objects.filter(
            date_reserved=timezone.localdate()
        ).exclude(status='Rejected')

    elif filter_type == 'rejected':
        reservations = Reservation.objects.filter(status='Rejected')

    else:  # 'all' or unknown filter
        reservations = Reservation.objects.all()

    # Process reservations for display
    reservations_data = []
    for res in reservations:
        # Default to 'Complete' if all requirements are met
        if res.status == 'Rejected':
            status = 'Rejected'
        elif not res.billing_file:
            status = 'Needs Billing'
        elif not res.receipt_file:
            status = 'Needs Payment Verification'
        elif not res.security_pass_pdf:
            status = 'Needs Security Pass'
        else:
            status = 'Complete'  # Everything is in place

        reservations_data.append({
            'id': res.id,
            'reference': f'RES-{res.id:06d}',
            'facility': res.facility_use,
            'date': res.date,
            'status': status,
            'has_billing': bool(res.billing_file),
            'has_payment': bool(res.receipt_file),
            'has_pass': bool(res.security_pass_pdf),
            'receipt_file': res.receipt_file  # Include the receipt file for linking
        })

    context = {
        'reservations': reservations_data,
        'current_filter': filter_type
    }
    return render(request, 'superuser/superuser_managereservations.html', context)



@login_required
@user_passes_test(is_superuser)
def verify_payment(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    if request.method == 'POST':
        # Handle payment verification logic
        reservation.payment_verified = True
        reservation.save()
        return redirect('superuser_portal:manage_reservations')
    return render(request, 'superuser/verify_payment.html', {'reservation': reservation})

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
    time_templates = TimeSlotTemplate.objects.all().prefetch_related('slots')
    blocked_dates = BlockedDate.objects.all().select_related('facility')
    
    context = {
        'facilities': facilities,
        'time_templates': time_templates,
        'blocked_dates': blocked_dates
    }
    
    return render(request, 'superuser/superuser_systemsettings.html', context)

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
        return JsonResponse({'status': 'success'})
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
        return JsonResponse({'status': 'success'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
@user_passes_test(is_superuser)
def manage_blocked_dates(request):
    if request.method == 'POST':
        facility_id = request.POST.get('facility')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')
        
        BlockedDate.objects.create(
            facility_id=facility_id,
            start_date=start_date,
            end_date=end_date,
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
        return JsonResponse({'status': 'success'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
@user_passes_test(is_superuser)
def user_roles(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'superuser/superuser_userroles.html', {'users': users})

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
        
        # TODO: Send email with new password
        # For now, we'll return the password in the response
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
    return render(request, 'superuser/superuser_profile.html')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


@login_required
@user_passes_test(is_superuser)
def reservation_details(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id)


    if request.method == 'POST':
        billing_file = request.FILES.get('billing_file')
        amount = request.POST.get('amount')
        due_date = request.POST.get('due_date')

        if billing_file and amount and due_date:
            reservation.billing_file = billing_file
            reservation.amount = amount
            reservation.due_date = due_date
            reservation.billing_uploaded = True
            reservation.save()
            messages.success(request, 'Billing details uploaded successfully.')
        else:
            messages.error(request, 'Please fill in all the fields.')

        return redirect('superuser_portal:reservation_details', reservation_id=reservation_id)

    return render(request, 'superuser_portal/reservation_details.html', {'reservation': reservation})

@user_passes_test(is_superuser)
def pending_reservations(request):
    reservations = Reservation.objects.filter(status='Pending')
    return render(request, 'superuser_portal/pending_reservations.html', {'reservations': reservations})
   


def reservation_details_json(request, reservation_id):
    """
    Return reservation details in JSON format including billing and security pass info
    """
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # Get billing information
    billing_info = None
    if reservation.billing_file:
        try:
            billing_info = {
                'statement_url': reservation.billing_file.url,
                'amount': float(reservation.amount) if reservation.amount else None,
                'due_date': reservation.due_date.strftime('%Y-%m-%d') if hasattr(reservation.due_date, 'strftime') else str(reservation.due_date),
                'status': 'issued'
            }
        except AttributeError:
            # Handle case where due_date might be a string
            billing_info = {
                'statement_url': reservation.billing_file.url,
                'amount': float(reservation.amount) if reservation.amount else None,
                'due_date': str(reservation.due_date) if reservation.due_date else None,
                'status': 'issued'
            }
    
    # Get security pass information
    pass_info = None
    if reservation.security_pass_file:
        pass_info = {
            'file_url': reservation.security_pass_file.url,
            'notes': reservation.security_pass_notes if hasattr(reservation, 'security_pass_notes') else '',
            'status': 'uploaded'
        }
    
    # Prepare the response data
    data = {
        'id': reservation.id,
        'reference': reservation.security_pass_id,  # Using security_pass_id as reference
        'status': reservation.status,
        'billing': billing_info,
        'pass': pass_info,
    }
    
    return JsonResponse(data)

@user_passes_test(is_superuser)
def approve_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    reservation.status = "Approved"
    reservation.save()
    messages.success(request, "Reservation approved.")
    return redirect('pending_reservations')

@csrf_exempt  # optional if using @csrf_protect and CSRF token
def reject_reservation(request, reservation_id):
    if request.method == 'POST':
        reservation = get_object_or_404(Reservation, id=reservation_id)
        reservation.status = 'Rejected'
        reservation.save()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@user_passes_test(is_superuser)
def upload_billing(request, reservation_id):
    """
    View function to handle uploading billing statements for reservations
    """
    logger = logging.getLogger(__name__)
    
    try:
        reservation = get_object_or_404(Reservation, id=reservation_id)
        
        if request.method == 'POST':
            try:
                billing_file = request.FILES.get('billing_file')
                amount = request.POST.get('amount')
                due_date_str = request.POST.get('due_date')
                
                # Log received data for debugging (excluding file contents)
                logger.debug(f"Received billing data - amount: {amount}, due_date: {due_date_str}, file: {billing_file.name if billing_file else None}")
                
                if not all([billing_file, amount, due_date_str]):
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Missing required billing information.'
                    }, status=400)
                
                # Update reservation billing fields directly
                reservation.billing_file = billing_file
                
                # Convert amount to Decimal with proper error handling
                try:
                    reservation.amount = Decimal(amount)
                except InvalidOperation:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Invalid amount format: {amount}'
                    }, status=400)
                
                # Convert due_date string to a proper date object
                try:
                    # Parse the date string from the form (YYYY-MM-DD format)
                    reservation.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
                except ValueError:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Invalid date format: {due_date_str}. Expected YYYY-MM-DD.'
                    }, status=400)
                
                # Update status if needed
                if reservation.status == 'Pending' or reservation.status == 'Approved':
                    reservation.status = 'Billing Uploaded'
                
                reservation.save()
                
                logger.debug(f"Successfully saved billing for reservation {reservation_id}")
                
                # Return success response with billing info
                return JsonResponse({
                    'status': 'success',
                    'billing': {
                        'statement_url': reservation.billing_file.url,
                        'amount': float(reservation.amount),
                        'due_date': reservation.due_date.strftime('%Y-%m-%d'),
                        'status': 'issued'
                    }
                })
            except Exception as e:
                error_msg = f"Error processing billing for reservation {reservation_id}: {str(e)}"
                logger.error(f"{error_msg}\n{traceback.format_exc()}")
                return JsonResponse({
                    'status': 'error',
                    'message': f'Server error: {str(e)}'
                }, status=500)
        
        # Handle GET requests or other methods
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method. Only POST is supported.'
        }, status=405)
        
    except Exception as e:
        error_msg = f"Unexpected error in upload_billing view: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        return JsonResponse({
            'status': 'error',
            'message': 'An unexpected error occurred.'
        }, status=500)

@user_passes_test(is_superuser)
def verify_receipt(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == "approve":
            messages.success(request, "Receipt approved.")
        elif action == "reject":
            reservation.receipt_file = None
            reservation.save()
            messages.warning(request, "Receipt rejected.")
        return redirect('pending_reservations')
    return render(request, 'superuser_portal/verify_receipt.html', {'reservation': reservation})

@login_required
def upload_security_pass(request, reservation_id):
    """Upload security pass by the superuser"""
    # Check if the user is a superuser
    if not request.user.is_superuser:
        return JsonResponse({
            'status': 'error',
            'message': 'Permission denied'
        }, status=403)
        
    reservation = get_object_or_404(Reservation, id=reservation_id)

    if request.method == 'POST':
        pass_file = request.FILES.get('pass_file')

        if pass_file:
            # Save the file to the reservation
            reservation.security_pass_pdf = pass_file
            
            # Update the reservation status - ensuring it moves to Security Pass Issued
            if reservation.status in ['Payment Approved', 'Needs Security Pass', 'Billing Uploaded']:
                reservation.status = 'Security Pass Issued'
            
            reservation.save()

            # Return a proper JSON response
            return JsonResponse({
                'status': 'success',
                'pass': {
                    'file_url': reservation.security_pass_pdf.url,
                    'status': 'uploaded'
                },
                'reservation_status': reservation.status
            })
        
        return JsonResponse({
            'status': 'error', 
            'message': 'No file uploaded.'
        })

    # Handle GET requests or other methods
    return JsonResponse({
        'status': 'error', 
        'message': 'Invalid request method. Only POST is supported.'
    })

def reservation_details_json(request, reservation_id):
    """
    Return reservation details in JSON format including billing and security pass info
    """
    # Check if the user is a superuser
    if not request.user.is_superuser:
        return JsonResponse({
            'status': 'error',
            'message': 'Permission denied'
        }, status=403)
        
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # Get billing information
    billing_info = None
    if reservation.billing_file:
        try:
            billing_info = {
                'statement_url': reservation.billing_file.url,
                'amount': float(reservation.amount) if reservation.amount else None,
                'due_date': reservation.due_date.strftime('%Y-%m-%d') if hasattr(reservation.due_date, 'strftime') else str(reservation.due_date),
                'status': 'issued'
            }
        except AttributeError:
            # Handle case where due_date might be a string
            billing_info = {
                'statement_url': reservation.billing_file.url,
                'amount': float(reservation.amount) if reservation.amount else None,
                'due_date': str(reservation.due_date) if reservation.due_date else None,
                'status': 'issued'
            }
    
    # Get security pass information
    pass_info = None
    if reservation.security_pass_pdf:
        pass_info = {
            'file_url': reservation.security_pass_pdf.url,
            'status': 'uploaded'
        }
        
        # Add completed form information if it exists
        if reservation.completed_form:
            pass_info['completed_form_url'] = reservation.completed_form.url
            pass_info['completed_status'] = 'submitted'
    
    # Prepare the response data
    data = {
        'id': reservation.id,
        'reference': reservation.security_pass_id if hasattr(reservation, 'security_pass_id') else f'R-{reservation.id}',
        'status': reservation.status,
        'billing': billing_info,
        'pass': pass_info,
    }
    
    return JsonResponse(data)



@user_passes_test(is_superuser)
def review_completed_form(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')  # Approved / Rejected / Pending
        reservation.status = status
        reservation.save()
        messages.success(request, f"Form marked as {status}.")
        return redirect('pending_reservations')
    return render(request, 'superuser_portal/review_form.html', {'reservation': reservation})


@user_passes_test(is_superuser)
def delete_billing(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    if reservation.billing_file:
        reservation.billing_file.delete()
        reservation.billing_file = None
        reservation.amount = None
        reservation.due_date = None
        reservation.status = 'Needs Billing'
        reservation.save()
        messages.success(request, 'Billing file deleted.')
    return redirect('superuser_portal:manage_reservations')