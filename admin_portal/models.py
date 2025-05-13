from django.db import models
from django.contrib.auth.models import User

# Profile model for user details
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    course = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    def __str__(self):
        return self.user.username

# Reservation model to store reservation details
class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_reservations')
    title = models.CharField(max_length=200)  # Reservation title
    start_time = models.TimeField(default="00:00:00")
    end_time = models.TimeField(default="00:00:00")# End time of the reservation
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')])
    organization = models.CharField(max_length=100, blank=True, null=True)  # Optional organization field
    representative = models.CharField(max_length=100, blank=True, null=True)  # Optional representative name
    contact_number = models.CharField(max_length=15, blank=True, null=True)  # Optional contact number
    event_type = models.CharField(max_length=50, blank=True, null=True)  # Type of event
    insider_count = models.IntegerField(default=0)  # Number of insiders
    outsider_count = models.IntegerField(default=0)  # Number of outsiders

    # Optional fields for additional details
    facilities_needed = models.JSONField(blank=True, null=True)  # Facilities requested in JSON format
    manpower_needed = models.JSONField(blank=True, null=True)  # Manpower required in JSON format
    reasons = models.TextField(blank=True, null=True)  # Reason for the reservation

    def __str__(self):
        return f"{self.user.username} - {self.title}"
