from django.contrib import admin
from .models import Reservation

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'facility', 'date', 'status', 'formatted_time_slot', 'created_at')
    list_filter = ('status', 'facility', 'date')
    search_fields = ('user__username', 'user__email', 'facility', 'organization')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Reservation Status', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
        ('Reservation Details', {
            'fields': ('facility', 'date', 'start_time', 'end_time')
        }),
        ('Event Information', {
            'fields': ('organization', 'representative', 'event_type', 'insider_count', 'outsider_count')
        }),
        ('Resource Requirements', {
            'fields': ('facilities_needed', 'manpower_needed')
        }),
        ('Documents', {
            'fields': ('billing_statement', 'payment_receipt', 'security_pass')
        }),
        ('Admin Notes', {
            'fields': ('admin_notes', 'rejection_reason')
        }),
    )

    def formatted_time_slot(self, obj):
        return f"{obj.start_time.strftime('%I:%M %p')} - {obj.end_time.strftime('%I:%M %p')}"
    formatted_time_slot.short_description = 'Time Slot'