import os
from rest_framework import serializers

from accounts.models import ProfileModel
from core.constants import MAX_AVATAR_SIZE


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for ProfileModel.
    """

    lastName = serializers.CharField(
        source="last_name",
        required=True,
        min_length=2,
        max_length=30,
        error_messages={
            "required": "Last name is required",
            "min_length": "Last name must be at least 2 characters",
            "max_length": "Last name must be at most 30 characters",
        },
    )

    firstName = serializers.CharField(
        source="first_name",
        required=True,
        min_length=2,
        max_length=30,
        error_messages={
            "required": "First name is required",
            "min_length": "First name must be at least 2 characters",
            "max_length": "First name must be at most 30 characters",
        },
    )

    avatar = serializers.ImageField(
        required=False,
        allow_null=True,
        error_messages={
            "invalid": "Uploaded file must be a valid image.",
        },
    )

    class Meta:
        model = ProfileModel

        fields = [
            "avatar",
            "lastName",
            "firstName",
        ]

        read_only_fields = [
            "id",
            "user",
            "updated_at",
            "created_at",
        ]

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
