import pytest
from datetime import date, time, timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError

from bookings.models import Resource, Booking
from users.models import User


# ── Model Tests ──────────────────────────────────────────────────────────


class TestResourceModel:
    def test_create_resource(self, resource):
        assert resource.name == "Conference Room A"
        assert resource.is_available is True
        assert resource.capacity == 10

    def test_str_representation(self, resource):
        assert "Conference Room A" in str(resource)
        assert "Meeting Room" in str(resource)


class TestBookingModel:
    def test_create_booking(self, booking):
        assert booking.status == "PENDING"
        assert booking.notes == "Test booking"

    def test_get_duration_hours(self, booking):
        assert booking.get_duration_hours() == 2.0

    def test_calculate_total_price(self, booking):
        price = booking.calculate_total_price()
        assert price == Decimal("50.00")

    def test_calculate_total_price_no_price(self, user, db):
        resource = Resource.objects.create(
            name="Free Room",
            resource_type="ROOM",
            is_available=True,
            price_per_hour=None,
        )
        future_date = date.today() + timedelta(days=7)
        booking = Booking.objects.create(
            user=user,
            resource=resource,
            booking_date=future_date,
            start_time=time(10, 0),
            end_time=time(12, 0),
        )
        assert booking.calculate_total_price() == 0

    def test_is_conflicting(self, booking, user, resource):
        new_booking = Booking(
            user=user,
            resource=resource,
            booking_date=booking.booking_date,
            start_time=time(11, 0),
            end_time=time(13, 0),
        )
        assert new_booking.is_conflicting() is True

    def test_is_not_conflicting(self, booking, user, resource):
        new_booking = Booking(
            user=user,
            resource=resource,
            booking_date=booking.booking_date,
            start_time=time(14, 0),
            end_time=time(16, 0),
        )
        assert new_booking.is_conflicting() is False

    def test_clean_end_before_start(self, user, resource):
        future_date = date.today() + timedelta(days=7)
        booking = Booking(
            user=user,
            resource=resource,
            booking_date=future_date,
            start_time=time(14, 0),
            end_time=time(12, 0),
        )
        with pytest.raises(ValidationError) as exc_info:
            booking.full_clean()
        assert "end_time" in exc_info.value.message_dict

    def test_clean_past_date(self, user, resource):
        past_date = date.today() - timedelta(days=1)
        booking = Booking(
            user=user,
            resource=resource,
            booking_date=past_date,
            start_time=time(10, 0),
            end_time=time(12, 0),
        )
        with pytest.raises(ValidationError) as exc_info:
            booking.full_clean()
        assert "booking_date" in exc_info.value.message_dict

    def test_clean_unavailable_resource(self, user, db):
        resource = Resource.objects.create(
            name="Closed Room",
            resource_type="ROOM",
            is_available=False,
        )
        future_date = date.today() + timedelta(days=7)
        booking = Booking(
            user=user,
            resource=resource,
            booking_date=future_date,
            start_time=time(10, 0),
            end_time=time(12, 0),
        )
        with pytest.raises(ValidationError) as exc_info:
            booking.full_clean()
        assert "resource" in exc_info.value.message_dict

    def test_existing_booking_can_update_past(self, user, resource, db):
        """Existing bookings should be updatable even if their date is in the past."""
        future_date = date.today() + timedelta(days=1)
        booking = Booking.objects.create(
            user=user,
            resource=resource,
            booking_date=future_date,
            start_time=time(10, 0),
            end_time=time(12, 0),
            status="PENDING",
        )
        # Simulate date passing by directly updating the date
        Booking.objects.filter(pk=booking.pk).update(booking_date=date.today() - timedelta(days=1))
        booking.refresh_from_db()
        booking.status = "COMPLETED"
        booking.save()  # Should not raise


# ── API Tests ────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestBookingCRUD:
    list_url = "/api/bookings/list/"

    def test_create_booking(self, auth_client, resource):
        future_date = (date.today() + timedelta(days=5)).isoformat()
        data = {
            "resource": resource.id,
            "booking_date": future_date,
            "start_time": "09:00",
            "end_time": "10:00",
            "notes": "Test",
        }
        response = auth_client.post(self.list_url, data, format="json")
        assert response.status_code == 201

    def test_list_bookings(self, auth_client, booking):
        response = auth_client.get(self.list_url)
        assert response.status_code == 200
        assert response.data["count"] >= 1

    def test_retrieve_booking(self, auth_client, booking):
        response = auth_client.get(f"{self.list_url}{booking.id}/")
        assert response.status_code == 200
        assert response.data["id"] == booking.id

    def test_update_booking(self, auth_client, booking):
        data = {"notes": "Updated notes"}
        response = auth_client.patch(f"{self.list_url}{booking.id}/", data, format="json")
        assert response.status_code == 200

    def test_delete_booking(self, auth_client, booking):
        response = auth_client.delete(f"{self.list_url}{booking.id}/")
        assert response.status_code == 204

    def test_unauthenticated_cannot_list(self, api_client):
        response = api_client.get(self.list_url)
        assert response.status_code == 401


@pytest.mark.django_db
class TestBookingConflict:
    url = "/api/bookings/list/"

    def test_create_conflicting_booking(self, auth_client, booking, resource):
        data = {
            "resource": resource.id,
            "booking_date": booking.booking_date.isoformat(),
            "start_time": "11:00",
            "end_time": "13:00",
            "notes": "Conflict",
        }
        response = auth_client.post(self.url, data, format="json")
        assert response.status_code == 400


@pytest.mark.django_db
class TestBookingCancel:
    def test_cancel_booking(self, auth_client, booking):
        response = auth_client.post(f"/api/bookings/list/{booking.id}/cancel/")
        assert response.status_code == 200
        booking.refresh_from_db()
        assert booking.status == "CANCELLED"

    def test_cancel_already_cancelled(self, auth_client, booking):
        booking.status = "CANCELLED"
        booking.save()
        response = auth_client.post(f"/api/bookings/list/{booking.id}/cancel/")
        assert response.status_code == 400

    def test_cancel_completed_booking(self, auth_client, booking):
        booking.status = "COMPLETED"
        booking.save()
        response = auth_client.post(f"/api/bookings/list/{booking.id}/cancel/")
        assert response.status_code == 400


@pytest.mark.django_db
class TestBookingFilters:
    def test_upcoming_bookings(self, auth_client, booking):
        response = auth_client.get("/api/bookings/list/upcoming/")
        assert response.status_code == 200

    def test_past_bookings(self, auth_client, booking):
        response = auth_client.get("/api/bookings/list/past/")
        assert response.status_code == 200


@pytest.mark.django_db
class TestAdminStatusUpdate:
    def test_admin_can_update_status(self, admin_client, booking):
        response = admin_client.patch(
            f"/api/bookings/list/{booking.id}/update_status/",
            {"status": "CONFIRMED"},
            format="json",
        )
        assert response.status_code == 200
        booking.refresh_from_db()
        assert booking.status == "CONFIRMED"

    def test_non_admin_cannot_update_status(self, auth_client, booking):
        response = auth_client.patch(
            f"/api/bookings/list/{booking.id}/update_status/",
            {"status": "CONFIRMED"},
            format="json",
        )
        assert response.status_code == 403


@pytest.mark.django_db
class TestBookingIsolation:
    def test_user_cannot_see_other_bookings(self, api_client, booking, db):
        other_user = User.objects.create_user(
            email="other@example.com",
            username="other",
            password="OtherPass123!",
            first_name="Other",
            last_name="User",
        )
        api_client.force_authenticate(user=other_user)
        response = api_client.get("/api/bookings/list/")
        assert response.data["count"] == 0

    def test_admin_can_see_all_bookings(self, admin_client, booking):
        response = admin_client.get("/api/bookings/list/")
        assert response.data["count"] >= 1


# ── Resource API Tests ───────────────────────────────────────────────────


@pytest.mark.django_db
class TestResourceAPI:
    url = "/api/bookings/resources/"

    def test_list_resources_public(self, api_client, resource):
        response = api_client.get(self.url)
        assert response.status_code == 200

    def test_create_resource_admin(self, admin_client):
        data = {
            "name": "New Room",
            "resource_type": "ROOM",
            "capacity": 5,
            "is_available": True,
        }
        response = admin_client.post(self.url, data, format="json")
        assert response.status_code == 201

    def test_create_resource_non_admin(self, auth_client):
        data = {
            "name": "New Room",
            "resource_type": "ROOM",
            "capacity": 5,
        }
        response = auth_client.post(self.url, data, format="json")
        assert response.status_code == 403

    def test_available_filter(self, api_client, resource, db):
        Resource.objects.create(
            name="Unavailable Room",
            resource_type="ROOM",
            is_available=False,
        )
        response = api_client.get(f"{self.url}available/")
        assert response.status_code == 200
        names = [r["name"] for r in response.data]
        assert "Conference Room A" in names
        assert "Unavailable Room" not in names


@pytest.mark.django_db
class TestAvailabilityEndpoint:
    url = "/api/bookings/availability/"

    def test_check_availability(self, auth_client, resource, booking):
        response = auth_client.get(
            self.url,
            {
                "resource_id": resource.id,
                "date": booking.booking_date.isoformat(),
            },
        )
        assert response.status_code == 200
        assert len(response.data["booked_slots"]) == 1

    def test_missing_params(self, auth_client):
        response = auth_client.get(self.url)
        assert response.status_code == 400

    def test_invalid_resource(self, auth_client):
        response = auth_client.get(self.url, {"resource_id": 9999, "date": "2026-06-01"})
        assert response.status_code == 404
