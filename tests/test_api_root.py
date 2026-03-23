import pytest


@pytest.mark.django_db
class TestAPIRoot:
    url = "/api/"

    def test_api_root_returns_200(self, api_client):
        response = api_client.get(self.url)
        assert response.status_code == 200

    def test_api_root_contains_top_level_keys(self, api_client):
        response = api_client.get(self.url)
        assert "users" in response.data
        assert "bookings" in response.data
        assert "admin" in response.data

    def test_api_root_users_endpoints(self, api_client):
        response = api_client.get(self.url)
        users = response.data["users"]
        expected_keys = [
            "register",
            "login",
            "logout",
            "profile",
            "profile_update",
            "password_change",
            "password_reset_request",
            "password_reset_confirm",
            "token_refresh",
        ]
        for key in expected_keys:
            assert key in users, f"Missing user endpoint: {key}"

    def test_api_root_bookings_endpoints(self, api_client):
        response = api_client.get(self.url)
        bookings = response.data["bookings"]
        expected_keys = [
            "bookings_list",
            "resources_list",
            "availability_check",
        ]
        for key in expected_keys:
            assert key in bookings, f"Missing booking endpoint: {key}"

    def test_api_root_endpoints_are_absolute_urls(self, api_client):
        response = api_client.get(self.url)
        for endpoint_url in response.data["users"].values():
            assert endpoint_url.startswith("http"), (
                f"Expected absolute URL, got: {endpoint_url}"
            )
        for endpoint_url in response.data["bookings"].values():
            assert endpoint_url.startswith("http"), (
                f"Expected absolute URL, got: {endpoint_url}"
            )

    def test_api_root_returns_json(self, api_client):
        response = api_client.get(self.url)
        assert response["Content-Type"].startswith("application/json")

    def test_api_root_accessible_without_authentication(self, api_client):
        """API root should be public (AllowAny)."""
        response = api_client.get(self.url)
        assert response.status_code == 200

    def test_api_root_accessible_with_authentication(self, auth_client):
        """API root should also work for authenticated users."""
        response = auth_client.get(self.url)
        assert response.status_code == 200
        assert "users" in response.data

    def test_api_root_only_allows_get(self, api_client):
        """API root is decorated with @api_view(["GET"])."""
        assert api_client.post(self.url).status_code == 405
        assert api_client.put(self.url).status_code == 405
        assert api_client.patch(self.url).status_code == 405
        assert api_client.delete(self.url).status_code == 405

    def test_api_root_admin_url(self, api_client):
        response = api_client.get(self.url)
        assert response.data["admin"].endswith("/admin/")

    def test_api_root_no_extra_top_level_keys(self, api_client):
        """Ensure the response structure hasn't drifted unexpectedly."""
        response = api_client.get(self.url)
        assert set(response.data.keys()) == {"users", "bookings", "admin"}
