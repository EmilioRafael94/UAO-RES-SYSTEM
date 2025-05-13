from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import JsonResponse
from reservations.models import Reservation
from .models import Facility, TimeSlotTemplate, TimeSlot, BlockedDate
from datetime import timedelta
import json
from django.utils.crypto import get_random_string

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
    
    return render(request, 'superuser/superuser_dashboard.html', context)

@login_required
@user_passes_test(is_superuser)
def manage_reservations(request):
    # Get filter parameter
    filter_type = request.GET.get('filter', 'all')
    
    # Base queryset
    reservations = Reservation.objects.all()
    
    # Apply filters
    if filter_type == 'needs_billing':
        reservations = reservations.filter(billing_statement__isnull=True)
    elif filter_type == 'needs_payment':
        reservations = reservations.filter(
            billing_statement__isnull=False,
            payment_receipt__isnull=True
        )
    elif filter_type == 'needs_pass':
        reservations = reservations.filter(
            payment_receipt__isnull=False,
            security_pass__isnull=True
        )
    
    # Add metadata for each reservation
    reservations_data = []
    for res in reservations:
        status = 'Needs Billing'
        if res.billing_statement:
            status = 'Needs Payment Verification'
        if res.payment_receipt:
            status = 'Needs Security Pass'
        if res.security_pass:
            status = 'Complete'
            
        reservations_data.append({
            'id': res.id,
            'reference': f'RES-{res.id:06d}',
            'facility': res.facility,
            'date': res.date,
            'status': status,
            'has_billing': bool(res.billing_statement),
            'has_payment': bool(res.payment_receipt),
            'has_pass': bool(res.security_pass)
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

