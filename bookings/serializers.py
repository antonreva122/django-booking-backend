from rest_framework import serializers
from .models import Booking, Resource
from django.utils import timezone


class ResourceSerializer(serializers.ModelSerializer):
    """
    Serializer for Resource model.
    """
    class Meta:
        model = Resource
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for Booking model.
    """
    resource_details = ResourceSerializer(source='resource', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    duration_hours = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = (
            'id', 'user', 'user_email', 'resource', 'resource_details',
            'booking_date', 'start_time', 'end_time', 'status',
            'notes', 'duration_hours', 'total_price',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')
    
    def get_duration_hours(self, obj):
        try:
            return obj.get_duration_hours()
        except Exception as e:
            print(f"Error calculating duration for booking {obj.id}: {e}")
            return 0
    
    def get_total_price(self, obj):
        try:
            return float(obj.calculate_total_price())
        except Exception as e:
            print(f"Error calculating price for booking {obj.id}: {e}")
            return 0.0
    
    def validate_booking_date(self, value):
        """
        Validate that booking date is not in the past.
        """
        if value < timezone.now().date():
            raise serializers.ValidationError("Cannot book in the past.")
        return value
    
    def validate(self, data):
        """
        Validate booking data.
        """
        # Check if end_time is after start_time
        if data.get('start_time') and data.get('end_time'):
            if data['end_time'] <= data['start_time']:
                raise serializers.ValidationError({
                    "end_time": "End time must be after start time."
                })
        
        # Check resource availability
        resource = data.get('resource')
        if resource and not resource.is_available:
            raise serializers.ValidationError({
                "resource": "This resource is not currently available for booking."
            })
        
        return data


class BookingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating bookings.
    """
    class Meta:
        model = Booking
        fields = ('resource', 'booking_date', 'start_time', 'end_time', 'notes')
    
    def validate_booking_date(self, value):
        """
        Validate that booking date is not in the past.
        """
        if value < timezone.now().date():
            raise serializers.ValidationError("Cannot book in the past.")
        return value
    
    def validate(self, data):
        """
        Validate booking data and check for conflicts.
        """
        # Check if end_time is after start_time
        if data['end_time'] <= data['start_time']:
            raise serializers.ValidationError({
                "end_time": "End time must be after start time."
            })
        
        # Check resource availability
        if not data['resource'].is_available:
            raise serializers.ValidationError({
                "resource": "This resource is not currently available for booking."
            })
        
        # Check for booking conflicts
        conflicting_bookings = Booking.objects.filter(
            resource=data['resource'],
            booking_date=data['booking_date'],
            status__in=['PENDING', 'CONFIRMED']
        )
        
        for booking in conflicting_bookings:
            # Check for time overlap
            if (data['start_time'] < booking.end_time and data['end_time'] > booking.start_time):
                raise serializers.ValidationError({
                    "time": f"This time slot conflicts with an existing booking "
                           f"({booking.start_time} - {booking.end_time})."
                })
        
        return data


class BookingUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating bookings.
    """
    class Meta:
        model = Booking
        fields = ('booking_date', 'start_time', 'end_time', 'notes')
    
    def validate(self, data):
        """
        Validate that updated booking doesn't conflict with others.
        """
        instance = self.instance
        booking_date = data.get('booking_date', instance.booking_date)
        start_time = data.get('start_time', instance.start_time)
        end_time = data.get('end_time', instance.end_time)
        
        # Check if end_time is after start_time
        if end_time <= start_time:
            raise serializers.ValidationError({
                "end_time": "End time must be after start time."
            })
        
        # Check for booking conflicts (excluding current booking)
        conflicting_bookings = Booking.objects.filter(
            resource=instance.resource,
            booking_date=booking_date,
            status__in=['PENDING', 'CONFIRMED']
        ).exclude(pk=instance.pk)
        
        for booking in conflicting_bookings:
            # Check for time overlap
            if (start_time < booking.end_time and end_time > booking.start_time):
                raise serializers.ValidationError({
                    "time": f"This time slot conflicts with an existing booking "
                           f"({booking.start_time} - {booking.end_time})."
                })
        
        return data


class BookingStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for updating booking status (admin only).
    """
    class Meta:
        model = Booking
        fields = ('status', 'admin_notes')
