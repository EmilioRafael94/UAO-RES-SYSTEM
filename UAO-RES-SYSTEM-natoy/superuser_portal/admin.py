
# Register your models here.
from django.contrib import admin
from .models import Facility, TimeSlotTemplate, TimeSlot, BlockedDate

@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(TimeSlotTemplate)
class TimeSlotTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('template', 'start_time', 'end_time')
    list_filter = ('template',)

@admin.register(BlockedDate)
class BlockedDateAdmin(admin.ModelAdmin):
    list_display = ('date', 'reason', 'created_by', 'created_at')
    list_filter = ('date', 'created_by')
    search_fields = ('reason', 'created_by__username')
