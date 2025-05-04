from django.shortcuts import render
from reservations.views import make_reservation
from django.contrib.auth.decorators import login_required

def user_dashboard(request):
    # Your user-specific dashboard code here
    return render(request, 'user_dashboard.html')

def user_reservation(request):
    return make_reservation(request)
