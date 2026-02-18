from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet, ResourceViewSet, BookingAvailabilityView

router = DefaultRouter()
router.register(r'list', BookingViewSet, basename='booking')
router.register(r'resources', ResourceViewSet, basename='resource')

urlpatterns = [
    path('', include(router.urls)),
    path('availability/', BookingAvailabilityView.as_view(), name='booking-availability'),
]
