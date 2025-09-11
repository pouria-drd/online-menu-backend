import os
from django.utils import timezone
from rest_framework import serializers
from accounts.models import ProfileModel
from accounts.constants import MAX_AVATAR_SIZE


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile.
    - Maps snake_case model fields to camelCase API fields.
    - Ensures valid birthday (not in future, not before 1900).
    - Handles avatar upload + returns absolute URL.
    """

    firstName = serializers.CharField(
        source="first_name", required=False, allow_blank=True
    )
    lastName = serializers.CharField(
        source="last_name", required=False, allow_blank=True
    )

    # updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)
    # createdAt = serializers.DateTimeField(source="created_at", read_only=True)

    # Avatar: writable for upload
    avatar = serializers.ImageField(
        required=False,
        allow_null=True,
        error_messages={
            "invalid": "Uploaded file must be a valid image.",
        },
    )

    birthday = serializers.DateField(
        required=False,
        error_messages={
            "invalid": "Birthday must be a valid date (YYYY-MM-DD).",
        },
    )

    class Meta:
        model = ProfileModel
        fields = [
            # "id",
            "bio",
            "gender",
            "birthday",
            "firstName",
            "lastName",
            "avatar",
            # "updatedAt",
            # "createdAt",
        ]
        read_only_fields = [
            "id",
            "user",
            "updatedAt",
            "createdAt",
        ]
        extra_kwargs = {
            "bio": {"required": False, "allow_blank": True},
            "gender": {"required": False},
        }

    # --------------------------
    # Field-level validation
    # --------------------------

    def validate_birthday(self, value):
        today = timezone.now().date()
        if value.year < 1900:
            raise serializers.ValidationError(
                "Please provide a valid birthday (>= 1900).", code="birthday_too_old"
            )
        if value > today:
            raise serializers.ValidationError(
                "Birthday cannot be in the future.", code="birthday_in_future"
            )
        return value

    def validate_avatar(self, value):
        if value and hasattr(value, "size"):
            if value.size > MAX_AVATAR_SIZE:
                raise serializers.ValidationError(
                    f"Avatar size must be under {MAX_AVATAR_SIZE / 1024 / 1024}MB.",
                    code="avatar_too_large",
                )
            valid_extensions = [".jpg", ".jpeg", ".png", ".webp"]
            ext = os.path.splitext(value.name)[1].lower()
            if ext not in valid_extensions:
                raise serializers.ValidationError(
                    f"Unsupported file type. Allowed: {', '.join(valid_extensions)}",
                    code="invalid_file_type",
                )
        return value
