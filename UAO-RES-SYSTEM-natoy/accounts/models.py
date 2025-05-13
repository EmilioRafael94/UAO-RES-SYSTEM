from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    course = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20)
    id_upload = models.FileField(upload_to='uploads/ids/', null=True, blank=True)

    def __str__(self):
        return self.user.username
