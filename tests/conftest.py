import pytest
from datetime import date, time, timedelta
from decimal import Decimal
from rest_framework.test import APIClient

from users.models import User
from bookings.models import Resource, Booking


@pytest.fixture(autouse=True)
def _disable_security_and_throttle(settings):
    settings.SECURE_SSL_REDIRECT = False
    from django.core.cache import cache

    cache.clear()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="testuser@example.com",
        username="testuser",
        password="TestPass123!",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        email="admin@example.com",
        username="admin",
        password="AdminPass123!",
        first_name="Admin",
        last_name="User",
    )


@pytest.fixture
def resource(db):
    return Resource.objects.create(
        name="Conference Room A",
        description="A large conference room",
        resource_type="ROOM",
        capacity=10,
        is_available=True,
        location="Building 1, Floor 2",
        price_per_hour=Decimal("25.00"),
    )


@pytest.fixture
def booking(db, user, resource):
    future_date = date.today() + timedelta(days=7)
    return Booking.objects.create(
        user=user,
        resource=resource,
        booking_date=future_date,
        start_time=time(10, 0),
        end_time=time(12, 0),
        status="PENDING",
        notes="Test booking",
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client
