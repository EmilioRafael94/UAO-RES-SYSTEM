from django import forms
from .models import Reservation

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['facility', 'date', 'time_slot']

class BillingForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['billing_statement']

class PaymentVerificationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['payment_receipt', 'security_pass']
