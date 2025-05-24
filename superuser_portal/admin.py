from django.contrib import admin
from .models import Profile, Facility, TimeSlotTemplate, TimeSlot, BlockedDate

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'phone')

@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'created_at')

@admin.register(TimeSlotTemplate)
class TimeSlotTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('template', 'start_time', 'end_time')

@admin.register(BlockedDate)
class BlockedDateAdmin(admin.ModelAdmin):
    list_display = ('facility', 'date', 'start_time', 'end_time', 'reason', 'created_by', 'created_at')
    list_filter = ('facility', 'date', 'created_by')
    search_fields = ('facility__name', 'reason')
