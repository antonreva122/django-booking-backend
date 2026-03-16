import pytest
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.django_db
class TestUploadProfileImage:
    url = "/api/users/profile/image/upload/"

    def test_no_image_provided(self, auth_client):
        response = auth_client.post(self.url)
        assert response.status_code == 400
        assert "No image file" in response.data["error"]

    def test_invalid_file_type(self, auth_client):
        file = SimpleUploadedFile("test.txt", b"not an image", content_type="text/plain")
        response = auth_client.post(self.url, {"image": file}, format="multipart")
        assert response.status_code == 400
        assert "Invalid file type" in response.data["error"]

    def test_file_too_large(self, auth_client):
        # Create a file just over 5MB
        large_data = b"x" * (5 * 1024 * 1024 + 1)
        file = SimpleUploadedFile("big.jpg", large_data, content_type="image/jpeg")
        response = auth_client.post(self.url, {"image": file}, format="multipart")
        assert response.status_code == 400
        assert "too large" in response.data["error"]

    @patch("users.image_views.cloudinary.uploader.upload")
    def test_upload_success(self, mock_upload, auth_client, user):
        mock_upload.return_value = {"secure_url": "https://cdn.example.com/img.jpg"}
        file = SimpleUploadedFile("photo.jpg", b"\xff\xd8\xff\xe0", content_type="image/jpeg")
        response = auth_client.post(self.url, {"image": file}, format="multipart")
        assert response.status_code == 200
        assert response.data["profile_image"] == "https://cdn.example.com/img.jpg"
        user.refresh_from_db()
        assert user.profile_image == "https://cdn.example.com/img.jpg"

    @patch("users.image_views.cloudinary.uploader.upload")
    @patch("users.image_views.cloudinary.uploader.destroy")
    def test_upload_replaces_old_image(self, mock_destroy, mock_upload, auth_client, user):
        user.profile_image = "https://cdn.example.com/old.jpg"
        user.save()
        mock_upload.return_value = {"secure_url": "https://cdn.example.com/new.jpg"}
        file = SimpleUploadedFile("photo.jpg", b"\xff\xd8\xff\xe0", content_type="image/jpeg")
        response = auth_client.post(self.url, {"image": file}, format="multipart")
        assert response.status_code == 200
        mock_destroy.assert_called_once()

    @patch("users.image_views.cloudinary.uploader.upload", side_effect=Exception("API down"))
    def test_upload_cloudinary_failure(self, mock_upload, auth_client):
        file = SimpleUploadedFile("photo.jpg", b"\xff\xd8\xff\xe0", content_type="image/jpeg")
        response = auth_client.post(self.url, {"image": file}, format="multipart")
        assert response.status_code == 500
        assert "Failed to upload" in response.data["error"]

    def test_unauthenticated(self, api_client):
        response = api_client.post(self.url)
        assert response.status_code == 401


@pytest.mark.django_db
class TestDeleteProfileImage:
    url = "/api/users/profile/image/delete/"

    def test_no_image_to_delete(self, auth_client, user):
        user.profile_image = None
        user.save()
        response = auth_client.delete(self.url)
        assert response.status_code == 400
        assert "No profile image" in response.data["error"]

    @patch("users.image_views.cloudinary.uploader.destroy")
    def test_delete_success(self, mock_destroy, auth_client, user):
        user.profile_image = "https://cdn.example.com/img.jpg"
        user.save()
        response = auth_client.delete(self.url)
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.profile_image is None
        mock_destroy.assert_called_once()

    @patch("users.image_views.cloudinary.uploader.destroy", side_effect=Exception("API down"))
    def test_delete_cloudinary_failure(self, mock_destroy, auth_client, user):
        user.profile_image = "https://cdn.example.com/img.jpg"
        user.save()
        response = auth_client.delete(self.url)
        assert response.status_code == 500
        assert "Failed to delete" in response.data["error"]

    def test_unauthenticated(self, api_client):
        response = api_client.delete(self.url)
        assert response.status_code == 401
