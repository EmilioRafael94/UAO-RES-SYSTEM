from django import forms
from django.contrib.auth.models import User
from .models import Profile, Reservation

class UserUpdateForm(forms.ModelForm):
    # Form for updating user details like username and email
    class Meta:
        model = User
        fields = ['username', 'email']  # Fields you want to update

class ProfileUpdateForm(forms.ModelForm):
    # Form for updating profile details like course, phone, etc.
    class Meta:
        model = Profile
        fields = ['course', 'phone']  # Add any other fields you have in the Profile model
