from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, ProfileUpdateForm  # Make sure you have these forms imported
from django.contrib import messages

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
    # Replace SAMPLE_RESERVATIONS with actual query like:
    # reservations = Reservation.objects.filter(user=request.user)

    return render(request, 'user_portal/user_myreservation.html', {
        'reservations': SAMPLE_RESERVATIONS
    })

def user_makereservation(request):
    # Any logic for handling reservations, if needed
    return render(request, 'user_portal/user_makereservation.html')

def user_calendar(request):
    return render(request, 'user_portal/user_calendar.html')

@login_required
def user_dashboard(request):
    return render(request, 'user_portal/user_dashboard.html')

@login_required
def user_profile(request):
    return render(request, 'user_portal/user_profile.html')

@login_required
def update_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()  # Save user data
            profile_form.save()  # Save profile data
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('user_portal:user_profile')  # Redirect to the profile page after saving
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    
    return render(request, 'user_portal/user_profile.html', context)
