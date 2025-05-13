from django import forms
from django.contrib.auth.models import User
from user_portal.models import Profile

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    role = forms.ChoiceField(choices=[
        ('Student of XU', 'Student of XU'),
        ('Alumni/Guest', 'Alumni/Guest')
    ])

    phone = forms.CharField(required=True)
    course = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password1')
        confirm = cleaned_data.get('password2')

        if password and confirm and password != confirm:
            raise forms.ValidationError("Passwords do not match.")

        role = cleaned_data.get('role')
        email = cleaned_data.get('email')

        if role == 'Student of XU' and email and not email.endswith('@my.xu.edu.ph'):
            raise forms.ValidationError("Students must use a @my.xu.edu.ph email.")

        if role == 'Student of XU' and not cleaned_data.get('course'):
            raise forms.ValidationError("Course is required for students.")

        return cleaned_data
