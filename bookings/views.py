from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Booking, Resource
from .serializers import (
    BookingSerializer,
    BookingCreateSerializer,
    BookingUpdateSerializer,
    BookingStatusSerializer,
    ResourceSerializer,
)
from users.email_utils import send_booking_confirmation_email, send_booking_cancellation_email


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission: allow access only to booking owner or admin.
    """
    def has_object_permission(self, request, view, obj):
        # Admin can access all bookings
        if request.user.is_staff:
            return True
        # User can only access their own bookings
        return obj.user == request.user


class ResourceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing resources.
    """
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    
    def get_permissions(self):
        """
        Only admin can create, update, or delete resources.
        Anyone can view resources.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Get list of available resources.
        """
        available_resources = self.queryset.filter(is_available=True)
        serializer = self.get_serializer(available_resources, many=True)
        return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bookings.
    """
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        """
        Users see only their bookings, admins see all.
        """
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=user)
    
    def get_serializer_class(self):
        """
        Use different serializers for different actions.
        """
        if self.action == 'create':
            return BookingCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return BookingUpdateSerializer
        elif self.action == 'update_status':
            return BookingStatusSerializer
        return BookingSerializer
    
    def perform_create(self, serializer):
        """
        Set the user when creating a booking and send confirmation email.
        """
        booking = serializer.save(user=self.request.user)
        
        # Send booking confirmation email
        try:
            booking_details = {
                'booking_id': booking.id,
                'resource_name': booking.resource.name,
                'date': booking.booking_date.strftime('%B %d, %Y'),
                'start_time': booking.start_time.strftime('%I:%M %p'),
                'end_time': booking.end_time.strftime('%I:%M %p'),
            }
            send_booking_confirmation_email(
                user_email=self.request.user.email,
                booking_details=booking_details,
                user_name=self.request.user.get_full_name() or self.request.user.username
            )
        except Exception as e:
            # Log the error but don't fail the booking creation
            print(f"Failed to send booking confirmation email: {e}")
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def cancel(self, request, pk=None):
        """
        Cancel a booking and send cancellation email.
        """
        booking = self.get_object()
        
        # Check if booking can be cancelled
        if booking.status in ['CANCELLED', 'COMPLETED']:
            return Response(
                {'error': f'Cannot cancel a {booking.status.lower()} booking'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'CANCELLED'
        booking.save()
        
        # Send cancellation email
        try:
            booking_details = {
                'booking_id': booking.id,
                'resource_name': booking.resource.name,
                'date': booking.booking_date.strftime('%B %d, %Y'),
                'start_time': booking.start_time.strftime('%I:%M %p'),
            }
            send_booking_cancellation_email(
                user_email=request.user.email,
                booking_details=booking_details,
                user_name=request.user.get_full_name() or request.user.username
            )
        except Exception as e:
            # Log the error but don't fail the cancellation
            print(f"Failed to send cancellation email: {e}")
        
        serializer = self.get_serializer(booking)
        return Response({
            'message': 'Booking cancelled successfully',
            'booking': serializer.data
        })
    
    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAdminUser])
    def update_status(self, request, pk=None):
        """
        Update booking status (admin only).
        """
        booking = self.get_object()
        serializer = BookingStatusSerializer(booking, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': 'Booking status updated successfully',
            'booking': BookingSerializer(booking).data
        })
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """
        Get upcoming bookings for the current user.
        """
        today = timezone.now().date()
        upcoming_bookings = self.get_queryset().filter(
            booking_date__gte=today,
            status__in=['PENDING', 'CONFIRMED']
        )
        serializer = self.get_serializer(upcoming_bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def past(self, request):
        """
        Get past bookings for the current user.
        """
        today = timezone.now().date()
        past_bookings = self.get_queryset().filter(
            booking_date__lt=today
        )
        serializer = self.get_serializer(past_bookings, many=True)
        return Response(serializer.data)


class BookingAvailabilityView(APIView):
    """
    View to check availability for a resource on a specific date.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Get available time slots for a resource on a date.
        
        Query params:
        - resource_id: ID of the resource
        - date: Date in YYYY-MM-DD format
        """
        resource_id = request.query_params.get('resource_id')
        date_str = request.query_params.get('date')
        
        if not resource_id or not date_str:
            return Response(
                {'error': 'resource_id and date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            resource = Resource.objects.get(pk=resource_id)
        except Resource.DoesNotExist:
            return Response(
                {'error': 'Resource not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get all bookings for this resource on this date
        bookings = Booking.objects.filter(
            resource=resource,
            booking_date=date,
            status__in=['PENDING', 'CONFIRMED']
        ).order_by('start_time')
        
        booked_slots = [
            {
                'start_time': booking.start_time.strftime('%H:%M'),
                'end_time': booking.end_time.strftime('%H:%M')
            }
            for booking in bookings
        ]
        
        return Response({
            'resource': ResourceSerializer(resource).data,
            'date': date_str,
            'is_available': resource.is_available,
            'booked_slots': booked_slots
        })
