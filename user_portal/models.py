from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect

class Profile(models.Model):
    ROLE_CHOICES = [
        ('Student of XU', 'Student of XU'),
        ('Alumni/Guest', 'Alumni/Guest'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    course = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Student of XU')
    id_type = models.CharField(max_length=50, blank=True, null=True)
    id_upload = models.FileField(upload_to='id_uploads/', blank=True, null=True)

    def __str__(self):
        return self.user.username
   

 
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=50, default='general')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}"

def make_reservation(request):
    if request.method == 'POST':
        facility = request.POST.get('facility')
        facility_use = request.POST.get('facility_use')
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        organization = request.POST.get('organization')
        representative = request.POST.get('representative')
        event_type = request.POST.get('event_type')

        required_fields = [facility, facility_use, date, start_time, end_time, organization, representative, event_type]
        if not all(required_fields):
            messages.error(request, "Please fill in all required fields.")
            return redirect('user_portal:user_makereservation')

        # Proceed with reservation creation
        # ... (rest of the view logic)

    return redirect('user_portal:user_makereservation')