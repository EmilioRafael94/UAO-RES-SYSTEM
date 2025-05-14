from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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
   



class Reservation(models.Model):
    # Basic user info
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.CharField(max_length=255, default='Unknown')
    representative = models.CharField(max_length=255, default='Unknown')
    contact_number = models.CharField(max_length=15, default='N/A')

    # Reservation details
    date_reserved = models.DateField(default=timezone.now)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    insider_count = models.IntegerField(default=0)
    outsider_count = models.IntegerField(default=0)
    reasons = models.TextField(blank=True, null=True)
    event_type = models.CharField(max_length=255, blank=True, null=True)
    facility_use = models.CharField(max_length=100, default='General Use')

    # Multiple selection fields
    facilities_needed = models.JSONField(blank=True, null=True)
    manpower_needed = models.JSONField(blank=True, null=True)

    # Reservation status: tracks progress through the whole workflow
    status = models.CharField(max_length=50, default='Pending')  
    # Options: Pending, Approved, Rejected, Billing Uploaded, Payment Approved, Payment Rejected, Security Pass Issued, Completed

    # Billing info (uploaded by superuser)
    billing_file = models.FileField(upload_to='billing/', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    # User uploads proof of payment
    receipt_file = models.FileField(upload_to='receipts/', null=True, blank=True)

    # Security pass handling
    security_pass_id = models.CharField(max_length=10, default='R-1')  # You may update how this ID is generated if needed
    security_pass_pdf = models.FileField(upload_to='security_passes/', null=True, blank=True)
    completed_form = models.FileField(upload_to='completed_forms/', null=True, blank=True)
    security_pass_file = models.FileField(upload_to='security_passes/', null=True, blank=True)
    completed_security_form = models.FileField(upload_to='completed_security_forms/', null=True, blank=True)
    
    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)

    def is_receipt_uploaded(self):
        return bool(self.receipt_file)
        
    def is_security_pass_issued(self):
        return bool(self.security_pass_file)

    def __str__(self):
        facilities = ", ".join(self.facilities_needed or [])
        return f"Reservation for {self.organization} on {self.date} – Facilities: {facilities}"

    class Meta:
        unique_together = ('user', 'date', 'start_time', 'end_time')

    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}"

    class Meta:
        ordering = ['-created_at']

class BlockedDate(models.Model):
    date = models.DateField()
    reason = models.TextField()
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='user_blockeddate_set'  # Add this line
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Blocked {self.date} - {self.reason}"
