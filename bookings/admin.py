from django.contrib import admin
from .models import Booking, Resource


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'resource_type', 'capacity', 'is_available', 'created_at')
    list_filter = ('resource_type', 'is_available')
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'resource', 'booking_date', 'start_time', 'end_time', 'status', 'created_at')
    list_filter = ('status', 'booking_date', 'created_at')
    search_fields = ('user__email', 'resource__name', 'notes')
    ordering = ('-created_at',)
    date_hierarchy = 'booking_date'
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('user', 'resource', 'booking_date', 'start_time', 'end_time')
        }),
        ('Status & Details', {
            'fields': ('status', 'notes', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
