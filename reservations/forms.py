from django import forms
from .models import Reservation
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models
from superuser_portal.models import Facility

class ReservationForm(forms.ModelForm):
    # letter = forms.FileField(required=True, help_text='Upload your reservation request letter (PDF/DOCX).')
    facilities = forms.ModelMultipleChoiceField(queryset=Facility.objects.all(), widget=forms.CheckboxSelectMultiple, required=True)
    dates = models.JSONField(default=list, blank=True)
    
    class Meta:
        model = Reservation
        fields = [
            'facilities', 'dates', 'start_time', 'end_time',
            'organization', 'representative', 'event_type',
            'insider_count', 'outsider_count',
            'facilities_needed', 'manpower_needed',
            # 'letter',
        ]
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time', 'step': 3600}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'step': 3600}),
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
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        # Flexible hour validation: 1-8 hours between 07:00 and 15:00, or 24 hours (07:00 to 07:00 next day)
        if start_time and end_time:
            sh, sm = start_time.hour, start_time.minute
            eh, em = end_time.hour, end_time.minute
            # Only allow full-hour blocks, both times must be on the hour
            if not (
                (sh == 7 and eh == 7 and sm == 0 and em == 0) or
                (
                    sh >= 7 and sh <= 14 and eh >= 8 and eh <= 15 and
                    eh > sh and (eh - sh) <= 8 and (eh - sh) >= 1 and
                    sm == 0 and em == 0
                )
            ):
                raise ValidationError('Please select your reservation time in full hourly blocks only. For example, 15:00 to 19:00 is allowed (4 hours). Partial hours like 15:00 to 15:30 or 15:45 to 16:15 are not allowed. Use 24-hour format and make sure both start and end times fall exactly on the hour.\nAllowed start times: 07:00 to 14:00. Allowed end times: 08:00 to 15:00, or 07:00 next day for 24 hours.')
        
        # Add additional validations here if needed
        # Example: Check if the facility is available on the given date and time slot
        facility = cleaned_data.get('facility')
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if facility and date and start_time and end_time:
            # Validate time range
            if start_time >= end_time:
                raise ValidationError("End time must be after start time.")
            
            # Exclude self when editing
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