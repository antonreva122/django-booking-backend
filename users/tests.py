import pytest
from datetime import timedelta
from django.utils import timezone

from users.models import User, PasswordResetToken


# ── Model Tests ──────────────────────────────────────────────────────────


class TestUserModel:
    def test_create_user(self, user):
        assert user.email == "testuser@example.com"
        assert user.username == "testuser"
        assert user.check_password("TestPass123!")
        assert not user.is_staff
        assert not user.is_superuser

    def test_email_is_username_field(self, user):
        assert User.USERNAME_FIELD == "email"

    def test_str_returns_email(self, user):
        assert str(user) == "testuser@example.com"


class TestPasswordResetTokenModel:
    @pytest.fixture
    def valid_token(self, user):
        return PasswordResetToken.objects.create(
            user=user,
            token="valid-token-123",
            expires_at=timezone.now() + timedelta(hours=24),
        )

    @pytest.fixture
    def expired_token(self, user):
        return PasswordResetToken.objects.create(
            user=user,
            token="expired-token-456",
            expires_at=timezone.now() - timedelta(hours=1),
        )

    @pytest.fixture
    def used_token(self, user):
        return PasswordResetToken.objects.create(
            user=user,
            token="used-token-789",
            expires_at=timezone.now() + timedelta(hours=24),
            used=True,
        )

    def test_valid_token_is_valid(self, valid_token):
        assert valid_token.is_valid() is True

    def test_expired_token_is_invalid(self, expired_token):
        assert expired_token.is_valid() is False

    def test_used_token_is_invalid(self, used_token):
        assert used_token.is_valid() is False

    def test_str_representation(self, valid_token):
        assert "testuser@example.com" in str(valid_token)


# ── API Tests ────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestRegistrationAPI:
    url = "/api/users/register/"

    def test_register_success(self, api_client):
        data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "StrongPass123!",
            "password2": "StrongPass123!",
            "first_name": "New",
            "last_name": "User",
        }
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == 201
        assert "tokens" in response.data
        assert response.data["user"]["email"] == "newuser@example.com"

    def test_register_password_mismatch(self, api_client):
        data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "StrongPass123!",
            "password2": "DifferentPass123!",
            "first_name": "New",
            "last_name": "User",
        }
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == 400

    def test_register_duplicate_email(self, api_client, user):
        data = {
            "email": "testuser@example.com",
            "username": "anotheruser",
            "password": "StrongPass123!",
            "password2": "StrongPass123!",
            "first_name": "Another",
            "last_name": "User",
        }
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == 400


@pytest.mark.django_db
class TestLoginAPI:
    url = "/api/users/login/"

    def test_login_success(self, api_client, user):
        data = {"email": "testuser@example.com", "password": "TestPass123!"}
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == 200
        assert "tokens" in response.data
        assert response.data["user"]["email"] == "testuser@example.com"

    def test_login_wrong_password(self, api_client, user):
        data = {"email": "testuser@example.com", "password": "WrongPass!"}
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == 401

    def test_login_missing_fields(self, api_client):
        response = api_client.post(self.url, {}, format="json")
        assert response.status_code == 400


@pytest.mark.django_db
class TestLogoutAPI:
    url = "/api/users/logout/"

    def test_logout_success(self, auth_client, user):
        login_response = auth_client.post(
            "/api/users/login/",
            {"email": "testuser@example.com", "password": "TestPass123!"},
            format="json",
        )
        refresh_token = login_response.data["tokens"]["refresh"]
        response = auth_client.post(self.url, {"refresh_token": refresh_token}, format="json")
        assert response.status_code == 200
        assert response.data["message"] == "Logout successful"

    def test_logout_missing_token(self, auth_client):
        response = auth_client.post(self.url, {}, format="json")
        assert response.status_code == 400
        assert "refresh_token" in response.data["error"].lower()


@pytest.mark.django_db
class TestProfileAPI:
    url = "/api/users/profile/"

    def test_get_profile_authenticated(self, auth_client, user):
        response = auth_client.get(self.url)
        assert response.status_code == 200
        assert response.data["email"] == "testuser@example.com"

    def test_get_profile_unauthenticated(self, api_client):
        response = api_client.get(self.url)
        assert response.status_code == 401

    def test_update_profile(self, auth_client, user):
        data = {
            "username": "updateduser",
            "first_name": "Updated",
            "last_name": "Name",
        }
        response = auth_client.put("/api/users/profile/update/", data, format="json")
        assert response.status_code == 200
        assert response.data["user"]["first_name"] == "Updated"


@pytest.mark.django_db
class TestPasswordChangeAPI:
    url = "/api/users/password/change/"

    def test_change_password_success(self, auth_client, user):
        data = {
            "old_password": "TestPass123!",
            "new_password": "NewStrongPass456!",
            "new_password2": "NewStrongPass456!",
        }
        response = auth_client.post(self.url, data, format="json")
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.check_password("NewStrongPass456!")

    def test_change_password_wrong_old(self, auth_client, user):
        data = {
            "old_password": "WrongOldPass!",
            "new_password": "NewStrongPass456!",
            "new_password2": "NewStrongPass456!",
        }
        response = auth_client.post(self.url, data, format="json")
        assert response.status_code == 400

    def test_change_password_mismatch(self, auth_client, user):
        data = {
            "old_password": "TestPass123!",
            "new_password": "NewStrongPass456!",
            "new_password2": "DifferentPass789!",
        }
        response = auth_client.post(self.url, data, format="json")
        assert response.status_code == 400


@pytest.mark.django_db
class TestPasswordResetAPI:
    request_url = "/api/users/password/reset/"
    confirm_url = "/api/users/password/reset/confirm/"

    def test_reset_request_existing_email(self, api_client, user):
        response = api_client.post(
            self.request_url,
            {"email": "testuser@example.com"},
            format="json",
        )
        assert response.status_code == 200
        assert "If the email exists" in response.data["message"]

    def test_reset_request_nonexistent_email(self, api_client):
        response = api_client.post(
            self.request_url,
            {"email": "nobody@example.com"},
            format="json",
        )
        assert response.status_code == 200
        assert "If the email exists" in response.data["message"]

    def test_reset_confirm_valid_token(self, api_client, user):
        PasswordResetToken.objects.create(
            user=user,
            token="reset-token-abc",
            expires_at=timezone.now() + timedelta(hours=24),
        )
        data = {
            "token": "reset-token-abc",
            "new_password": "ResetPass789!",
            "new_password2": "ResetPass789!",
        }
        response = api_client.post(self.confirm_url, data, format="json")
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.check_password("ResetPass789!")

    def test_reset_confirm_expired_token(self, api_client, user):
        PasswordResetToken.objects.create(
            user=user,
            token="expired-reset-token",
            expires_at=timezone.now() - timedelta(hours=1),
        )
        data = {
            "token": "expired-reset-token",
            "new_password": "ResetPass789!",
            "new_password2": "ResetPass789!",
        }
        response = api_client.post(self.confirm_url, data, format="json")
        assert response.status_code == 400

    def test_reset_confirm_invalid_token(self, api_client):
        data = {
            "token": "nonexistent-token",
            "new_password": "ResetPass789!",
            "new_password2": "ResetPass789!",
        }
        response = api_client.post(self.confirm_url, data, format="json")
        assert response.status_code == 400
