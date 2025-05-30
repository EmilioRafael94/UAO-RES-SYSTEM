from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import Reservation
from .forms import ReservationForm

def group_required(group_name):
    def in_group(user):
        return user.groups.filter(name=group_name).exists()
    return user_passes_test(in_group)

@login_required
@group_required('User')
def make_reservation(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.date_reserved = timezone.localdate()
            reservation.save()
            messages.success(request, 'Reservation submitted successfully.')
            return redirect('user_dashboard')
    else:
        form = ReservationForm()
    return render(request, 'user_portal/make_reservation.html', {'form': form})

@login_required
@group_required('Admin')
def approve_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        reservation.status = new_status
        reservation.save()
        messages.success(request, f'Reservation updated to {new_status}.')
        return redirect('admin_dashboard')
    return render(request, 'admin_portal/approve_reservation.html', {'reservation': reservation})

@login_required
@group_required('Superuser')
def finalize_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if request.method == 'POST':
        reservation.status = 'Finalized'
        reservation.save()
        messages.success(request, 'Reservation finalized.')
        return redirect('superuser_dashboard')
    return render(request, 'superuser_portal/finalize_reservation.html', {'reservation': reservation})
