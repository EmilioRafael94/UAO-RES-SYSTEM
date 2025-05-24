from django import forms
from user_portal.models import Reservation

class BillingForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['billing_file', 'amount', 'due_date']

class SecurityPassForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['security_pass_pdf']
