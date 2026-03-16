import pytest


@pytest.mark.django_db
class TestAPIRoot:
    def test_api_root_returns_endpoints(self, api_client):
        response = api_client.get("/api/")
        assert response.status_code == 200
        assert "users" in response.data
        assert "bookings" in response.data
        assert "admin" in response.data
