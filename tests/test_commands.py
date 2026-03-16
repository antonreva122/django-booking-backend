import pytest
from datetime import date, time, timedelta
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command

from bookings.models import Booking
from users.models import User


@pytest.mark.django_db
class TestCompletePastBookings:
    def test_completes_past_pending_bookings(self, user, resource):
        future_date = date.today() + timedelta(days=1)
        booking = Booking.objects.create(
            user=user,
            resource=resource,
            booking_date=future_date,
            start_time=time(10, 0),
            end_time=time(12, 0),
            status="PENDING",
        )
        # Move date to past
        Booking.objects.filter(pk=booking.pk).update(booking_date=date.today() - timedelta(days=2))

        out = StringIO()
        call_command("complete_past_bookings", stdout=out)
        booking.refresh_from_db()
        assert booking.status == "COMPLETED"
        assert "1 past booking(s)" in out.getvalue()

    def test_does_not_touch_future_bookings(self, booking):
        out = StringIO()
        call_command("complete_past_bookings", stdout=out)
        booking.refresh_from_db()
        assert booking.status == "PENDING"
        assert "0 past booking(s)" in out.getvalue()

    def test_does_not_touch_already_cancelled(self, user, resource):
        future_date = date.today() + timedelta(days=1)
        booking = Booking.objects.create(
            user=user,
            resource=resource,
            booking_date=future_date,
            start_time=time(10, 0),
            end_time=time(12, 0),
            status="CANCELLED",
        )
        Booking.objects.filter(pk=booking.pk).update(booking_date=date.today() - timedelta(days=2))
        call_command("complete_past_bookings")
        booking.refresh_from_db()
        assert booking.status == "CANCELLED"


@pytest.mark.django_db
class TestCreateSuperuserFromEnv:
    @patch.dict(
        "os.environ",
        {
            "DJANGO_SUPERUSER_EMAIL": "superadmin@test.com",
            "DJANGO_SUPERUSER_PASSWORD": "SuperPass123!",
            "DJANGO_SUPERUSER_USERNAME": "superadmin",
        },
    )
    def test_creates_superuser(self):
        out = StringIO()
        call_command("create_superuser_from_env", stdout=out)
        user = User.objects.get(email="superadmin@test.com")
        assert user.is_superuser
        assert user.username == "superadmin"
        assert "created successfully" in out.getvalue()

    @patch.dict(
        "os.environ",
        {
            "DJANGO_SUPERUSER_EMAIL": "superadmin@test.com",
            "DJANGO_SUPERUSER_PASSWORD": "SuperPass123!",
        },
    )
    def test_uses_default_username(self):
        call_command("create_superuser_from_env")
        user = User.objects.get(email="superadmin@test.com")
        assert user.username == "admin"

    @patch.dict("os.environ", {}, clear=True)
    def test_missing_env_vars(self):
        out = StringIO()
        call_command("create_superuser_from_env", stdout=out)
        assert "must be set" in out.getvalue()

    @patch.dict(
        "os.environ",
        {
            "DJANGO_SUPERUSER_EMAIL": "superadmin@test.com",
            "DJANGO_SUPERUSER_PASSWORD": "SuperPass123!",
        },
    )
    def test_duplicate_email_skipped(self):
        User.objects.create_superuser(
            email="superadmin@test.com", username="existing", password="Pass123!"
        )
        out = StringIO()
        call_command("create_superuser_from_env", stdout=out)
        assert "already exists" in out.getvalue()
