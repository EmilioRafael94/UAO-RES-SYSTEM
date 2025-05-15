from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Reservation(models.Model):
    STATUS_CHOICES = (
        ('Pending', _('Pending')),
        ('Admin Approved', _('Admin Approved')),  # When 4 admins approve
        ('Billing Uploaded', _('Billing Uploaded')),
        ('Payment Pending', _('Payment Pending')),
        ('Payment Approved', _('Payment Approved')),
        ('Security Pass Issued', _('Security Pass Issued')),
        ('Completed', _('Completed')),
        ('Rejected', _('Rejected')),
        ('Cancelled', _('Cancelled')),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Admin approval tracking
    admin_approvals = models.JSONField(default=dict, blank=True)  # Store admin usernames and their approval timestamps
    admin_rejections = models.JSONField(default=dict, blank=True)  # Store admin usernames and their rejection reasons

    # Basic reservation info
    title = models.CharField(max_length=255, blank=True)
    start_time = models.TimeField(default="00:00:00")
    end_time = models.TimeField(default="00:00:00")
    contact_number = models.CharField(max_length=20, blank=True)
    reasons = models.TextField(blank=True)

    # Payment and documents
    billing_statement = models.FileField(upload_to='billing_statements/', null=True, blank=True)
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

    # Payment verification fields
    payment_verified = models.BooleanField(default=False)
    payment_verified_date = models.DateTimeField(null=True, blank=True)
    payment_verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, 
                                           null=True, blank=True, 
                                           related_name='verified_payments')
    payment_rejection_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Reservation by {self.user.username} - {self.facility} on {self.date} - {self.status}"
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = _('Reservation')
        verbose_name_plural = _('Reservations')

    @property
    def total_attendees(self):
        return self.insider_count + self.outsider_count
    
    @property
    def is_pending(self):
        return self.status == 'Pending'
    
    @property
    def is_admin_approved(self):
        return self.status == 'Admin Approved'
    
    @property
    def is_rejected(self):
        return self.status == 'Rejected'
    
    @property
    def is_cancelled(self):
        return self.status == 'Cancelled'

    @property
    def admin_approval_count(self):
        return len(self.admin_approvals or {})

    def add_admin_approval(self, admin_username, notes=''):
        """Add an admin approval to the reservation"""
        approvals = self.admin_approvals or {}
        approvals[admin_username] = {
            'timestamp': timezone.now().isoformat(),
            'notes': notes
        }
        self.admin_approvals = approvals
        
        # If we have 4 unique admin approvals, update status
        if len(approvals) >= 4:
            self.status = 'Admin Approved'
        
        self.save()

    def add_admin_rejection(self, admin_username, reason):
        """Add an admin rejection to the reservation"""
        rejections = self.admin_rejections or {}
        rejections[admin_username] = {
            'timestamp': timezone.now().isoformat(),
            'reason': reason
        }
        self.admin_rejections = rejections
        self.status = 'Rejected'
        self.rejection_reason = reason
        self.save()

    @property
    def approval_status(self):
        """Get the current approval status with clear, user-friendly messages"""
        if self.status == 'Pending':
            count = len(self.admin_approvals or {})
            return f"Waiting for admin approval ({count}/4)"
        elif self.status == 'Admin Approved':
            return "Approved by 4 admins - Awaiting billing invoice"
        elif self.status == 'Billing Uploaded':
            return "Billing invoice uploaded - Awaiting your payment receipt"
        elif self.status == 'Payment Pending':
            return "Payment receipt uploaded - Awaiting verification"
        elif self.status == 'Payment Approved':
            return "Payment verified - Awaiting security pass"
        elif self.status == 'Security Pass Issued':
            return "Security pass issued - Reservation complete"
        elif self.status == 'Rejected':
            return "Reservation rejected"
        elif self.status == 'Cancelled':
            return "Reservation cancelled"
        else:
            return self.status

    @property
    def admin_approval_details(self):
        """Get details of admin approvals"""
        approvals = self.admin_approvals or {}
        return [
            {
                'admin': admin,
                'timestamp': data.get('timestamp'),
                'notes': data.get('notes', '')
            }
            for admin, data in approvals.items()
        ]
