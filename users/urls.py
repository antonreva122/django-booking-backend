from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserProfileView,
    UserUpdateView,
    PasswordChangeView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    LogoutView,
)
from .image_views import upload_profile_image, delete_profile_image

urlpatterns = [
    # Authentication
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Profile Management
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("profile/update/", UserUpdateView.as_view(), name="profile_update"),
    path("profile/image/upload/", upload_profile_image, name="profile_image_upload"),
    path("profile/image/delete/", delete_profile_image, name="profile_image_delete"),
    path("password/change/", PasswordChangeView.as_view(), name="password_change"),
    # Password Reset
    path("password/reset/", PasswordResetRequestView.as_view(), name="password_reset_request"),
    path(
        "password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"
    ),
]
