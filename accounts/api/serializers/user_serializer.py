from rest_framework import serializers
from accounts.models import UserModel
from .user_profile_serializer import UserProfileSerializer
from .user_settings_serializer import UserSettingsSerializer


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the main User model.
    Includes nested profile and settings serializers as read-only fields.
    """

    profile = UserProfileSerializer(read_only=True)
    settings = UserSettingsSerializer(read_only=True)

    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = UserModel
        fields = [
            "id",
            "email",
            "username",
            "role",
            "createdAt",
            "updatedAt",
            "profile",
            "settings",
        ]
        read_only_fields = [
            "id",
            "role",
            "email",
            "status",
            "is_staff",
            "createdAt",
            "updatedAt",
            "deleted_at",
            "profile",
            "settings",
        ]
