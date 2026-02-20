from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


class Resource(models.Model):
    """
    Model representing a bookable resource (e.g., meeting room, equipment, facility).
    """
    RESOURCE_TYPES = [
        ('ROOM', 'Meeting Room'),
        ('EQUIPMENT', 'Equipment'),
        ('FACILITY', 'Facility'),
        ('SERVICE', 'Service'),
        ('OTHER', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES, default='OTHER')
    capacity = models.IntegerField(default=1, help_text="Maximum capacity or quantity")
    is_available = models.BooleanField(default=True)
    location = models.CharField(max_length=200, blank=True)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'resources'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_resource_type_display()})"


class Booking(models.Model):
    """
    Model representing a booking made by a user for a resource.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True, help_text="User notes for the booking")
    admin_notes = models.TextField(blank=True, help_text="Admin notes (not visible to user)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bookings'
        ordering = ['-booking_date', '-start_time']
        indexes = [
            models.Index(fields=['user', 'booking_date']),
            models.Index(fields=['resource', 'booking_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Booking #{self.id} - {self.resource.name} by {self.user.email} on {self.booking_date}"
    
    def clean(self):
        """
        Validate booking data.
        """
        errors = {}
        
        # Check if end_time is after start_time
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            errors['end_time'] = "End time must be after start time."
        
        # Check if booking date is not in the past
        if self.booking_date and self.booking_date < timezone.now().date():
            errors['booking_date'] = "Cannot book in the past."
        
        # Check if resource is available
        if hasattr(self, 'resource') and not self.resource.is_available:
            errors['resource'] = "This resource is not currently available for booking."
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def is_conflicting(self):
        """
        Check if this booking conflicts with existing bookings.
        """
        conflicting_bookings = Booking.objects.filter(
            resource=self.resource,
            booking_date=self.booking_date,
            status__in=['PENDING', 'CONFIRMED']
        ).exclude(pk=self.pk)
        
        for booking in conflicting_bookings:
            # Check for time overlap
            if (self.start_time < booking.end_time and self.end_time > booking.start_time):
                return True
        
        return False
    
    def get_duration_hours(self):
        """
        Calculate booking duration in hours.
        """
        from datetime import datetime, timedelta
        start = datetime.combine(self.booking_date, self.start_time)
        end = datetime.combine(self.booking_date, self.end_time)
        duration = end - start
        return duration.total_seconds() / 3600
    
    def calculate_total_price(self):
        """
        Calculate total price for the booking.
        """
        if self.resource.price_per_hour:
            from decimal import Decimal
            duration = Decimal(str(self.get_duration_hours()))
            return self.resource.price_per_hour * duration
        return 0
