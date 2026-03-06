import cloudinary.uploader
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_profile_image(request):
    """
    Upload profile image to Cloudinary and update user profile.
    """
    if "image" not in request.FILES:
        return Response({"error": "No image file provided"}, status=status.HTTP_400_BAD_REQUEST)

    image_file = request.FILES["image"]

    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
    if image_file.content_type not in allowed_types:
        return Response(
            {"error": "Invalid file type. Only JPEG, PNG, and WebP images are allowed."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate file size (max 5MB)
    max_size = 5 * 1024 * 1024  # 5MB
    if image_file.size > max_size:
        return Response(
            {"error": "File too large. Maximum size is 5MB."}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            image_file,
            folder="booking_system/profiles",
            transformation=[
                {"width": 400, "height": 400, "crop": "fill", "gravity": "face"},
                {"quality": "auto", "fetch_format": "auto"},
            ],
            resource_type="image",
        )

        # Get the secure URL
        image_url = upload_result.get("secure_url")

        # Update user profile
        user = request.user

        # Delete old image from Cloudinary if exists
        if user.profile_image:
            try:
                # Extract public_id from URL
                old_public_id = user.profile_image.split("/")[-1].split(".")[0]
                cloudinary.uploader.destroy(f"booking_system/profiles/{old_public_id}")
            except Exception:
                pass  # Ignore errors when deleting old image

        user.profile_image = image_url
        user.save()

        return Response(
            {"message": "Profile image uploaded successfully", "profile_image": image_url},
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"error": f"Failed to upload image: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_profile_image(request):
    """
    Delete the user's profile image.
    """
    user = request.user

    if not user.profile_image:
        return Response({"error": "No profile image to delete"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Extract public_id from URL and delete from Cloudinary
        public_id = user.profile_image.split("/")[-1].split(".")[0]
        cloudinary.uploader.destroy(f"booking_system/profiles/{public_id}")

        # Remove from user profile
        user.profile_image = None
        user.save()

        return Response(
            {"message": "Profile image deleted successfully"}, status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {"error": f"Failed to delete image: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
