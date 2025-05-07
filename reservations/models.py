from django.db import models
from django.contrib.auth.models import User

class Reservation(models.Model):
<<<<<<< HEAD
    user = models.ForeignKey(User, on_delete=models.CASCADE)
=======
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations_from_app1')
>>>>>>> 9727abc7ded92f45cf4b563c2e2cca99d4ede459
    status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    billing_statement = models.FileField(upload_to='billing_statements/', blank=True, null=True)

    # Add the missing fields
    payment_receipt = models.FileField(upload_to='receipts/', blank=True, null=True)
    security_pass = models.FileField(upload_to='passes/', blank=True, null=True)

    # Example of other fields you might already have
    facility = models.CharField(max_length=255)
    date = models.DateField()
    time_slot = models.TimeField()

    def __str__(self):
        return f"Reservation by {self.user.username} - {self.status}"
