from django import forms
from django.contrib.auth.models import User
from user_portal.models import Profile
from reservations.models import Reservation

# User update form (for logged-in users to update their account info)
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        self.fields['email'].disabled = True  # Email should not be editable


# Profile update form (used when updating profile, e.g. from settings)
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'profile_picture', 'course']

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Make 'course' uneditable if role is Alumni/Guest
        if instance and instance.role == "Alumni/Guest":
            self.fields['course'].disabled = True
        else:
            self.fields['course'].required = True


# User creation/edit form (used during registration or by admin)
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


# Full profile form (used during registration or by admin)
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'course', 'id_type', 'id_upload', 'role', 'profile_picture']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.TextInput(attrs={'class': 'form-control'}),
            'id_type': forms.Select(attrs={'class': 'form-control'}),
            'id_upload': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


# Reservation form (used for making reservations)
class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [
            'organization', 'representative', 'date_reserved', 'dates', 'start_time', 'end_time', 'facilities', 'facility_use', 'event_type'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
