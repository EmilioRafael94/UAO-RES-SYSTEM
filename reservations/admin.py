from django.contrib import admin
from .models import Reservation

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'facility', 'date', 'time_slot', 'status', 'created_at')
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
            'fields': ('facility', 'date', 'time_slot')
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