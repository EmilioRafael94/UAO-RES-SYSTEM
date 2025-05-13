from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Reservation(models.Model):
    STATUS_CHOICES = (
        ('Pending', _('Pending')),
        ('Approved', _('Approved')),
        ('Rejected', _('Rejected')),
        ('Cancelled', _('Cancelled')),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # NEW FIELDS ADDED
    title = models.CharField(max_length=255, blank=True)
    start_time = models.TimeField(default="00:00:00")
    end_time = models.TimeField(default="00:00:00")
    contact_number = models.CharField(max_length=20, blank=True)
    reasons = models.TextField(blank=True)

    # Payment and documents
    billing_statement = models.FileField(upload_to='billing_statements/', blank=True, null=True)
    payment_receipt = models.FileField(upload_to='receipts/', blank=True, null=True)
    security_pass = models.FileField(upload_to='passes/', blank=True, null=True)

    # Reservation details
    facility = models.CharField(max_length=255)
    facility_use = models.CharField(max_length=255, blank=True)
    date = models.DateField()
    date_reserved = models.DateField(null=True, blank=True)

    # Additional information
    organization = models.CharField(max_length=255, blank=True)
    representative = models.CharField(max_length=255, blank=True)
    event_type = models.CharField(max_length=100, blank=True)
    insider_count = models.IntegerField(default=0)
    outsider_count = models.IntegerField(default=0)
    facilities_needed = models.JSONField(default=dict, blank=True)
    manpower_needed = models.JSONField(default=dict, blank=True)

    # Admin comments and notes
    admin_notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)

    def __str__(self):
        return f"Reservation by {self.user.username} - {self.facility} on {self.date} - {self.status}"
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = _('Reservation')
        verbose_name_plural = _('Reservations')

    @property
    def time_slot(self):
        """Format the time slot as a string"""
        if self.start_time and self.end_time:
            return f"{self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"
        return ""

    @property
    def total_attendees(self):
        return self.insider_count + self.outsider_count
    
    @property
    def is_pending(self):
        return self.status == 'Pending'
    
    @property
    def is_approved(self):
        return self.status == 'Approved'
    
    @property
    def is_rejected(self):
        return self.status == 'Rejected'
    
    @property
    def is_cancelled(self):
        return self.status == 'Cancelled'
