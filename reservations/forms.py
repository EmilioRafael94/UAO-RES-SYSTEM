from django import forms
from .models import Reservation
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [
            'facility', 'date', 'start_time', 'end_time',
            'organization', 'representative', 'event_type',
            'insider_count', 'outsider_count',
            'facilities_needed', 'manpower_needed',
            'billing_statement', 'payment_receipt', 'security_pass'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'facilities_needed': forms.Textarea(attrs={'rows': 3}),
            'manpower_needed': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super(ReservationForm, self).__init__(*args, **kwargs)
        self.fields['insider_count'].widget.attrs.update({'min': '0'})
        self.fields['outsider_count'].widget.attrs.update({'min': '0'})
        
    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date < timezone.now().date():
            raise ValidationError("Reservation date cannot be in the past.")
        return date
    
    def clean(self):
        cleaned_data = super().clean()
        
        facility = cleaned_data.get('facility')
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if facility and date and start_time and end_time:
            if start_time >= end_time:
                raise ValidationError("End time must be after start time.")
            
            instance_id = self.instance.id if self.instance and self.instance.pk else None
            
            conflicting_reservations = Reservation.objects.filter(
                facility=facility,
                date=date,
                status='Approved'
            ).filter(
                (models.Q(start_time__lte=start_time) & models.Q(end_time__gt=start_time)) |
                (models.Q(start_time__lt=end_time) & models.Q(end_time__gte=end_time)) |
                (models.Q(start_time__gte=start_time) & models.Q(end_time__lte=end_time))
            )
            
            if instance_id:
                conflicting_reservations = conflicting_reservations.exclude(id=instance_id)
                
            if conflicting_reservations.exists():
                raise ValidationError(
                    f"This facility is already reserved for the selected date and time slot."
                )
        
        return cleaned_data

class AdminReservationUpdateForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [
            'status', 'admin_notes', 'rejection_reason'
        ]
        widgets = {
            'admin_notes': forms.Textarea(attrs={'rows': 3}),
            'rejection_reason': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        rejection_reason = cleaned_data.get('rejection_reason')
        
        if status == 'Rejected' and not rejection_reason:
            raise ValidationError("Please provide a reason for rejection.")
            
        return cleaned_data