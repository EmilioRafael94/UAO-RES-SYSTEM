from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')  # Changed related_name
    course = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    def __str__(self):
        return self.user.username

class Reservation(models.Model):
    facility = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.CharField(max_length=255, default='Unknown')  # Set default value
    representative = models.CharField(max_length=255, default='Unknown')  # Set default value
    contact_number = models.CharField(max_length=15, default='N/A')
    date_reserved = models.DateField(default=timezone.now)  # Set default to current date
    insider_count = models.IntegerField(default=0)
    outsider_count = models.IntegerField(default=0)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    reasons = models.TextField(blank=True, null=True)
    event_type = models.CharField(max_length=255, blank=True, null=True)
    facilities_needed = models.JSONField(blank=True, null=True)  # ✅ Change this
    manpower_needed = models.JSONField(blank=True, null=True)
    status = models.CharField(max_length=50, default='Pending')
    facility_use = models.CharField(max_length=100)

    class Meta:
        unique_together = ('facility', 'date', 'start_time', 'end_time')

    def __str__(self):
        return f"Reservation for {self.organization} on {self.date}"