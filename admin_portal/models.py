from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    course = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    def __str__(self):
        return self.user.username

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_reservations')
    title = models.CharField(max_length=200)
    start_time = models.TimeField(default="00:00:00")
    end_time = models.TimeField(default="00:00:00")
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')])
    organization = models.CharField(max_length=100, blank=True, null=True)
    representative = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    event_type = models.CharField(max_length=50, blank=True, null=True)
    insider_count = models.IntegerField(default=0)
    outsider_count = models.IntegerField(default=0)

    facilities_needed = models.JSONField(blank=True, null=True)
    manpower_needed = models.JSONField(blank=True, null=True)
    reasons = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"
