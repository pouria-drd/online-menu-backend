from rest_framework import serializers
from accounts.models import UserModel
from .user_profile_serializer import UserProfileSerializer
from .user_settings_serializer import UserSettingsSerializer


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    settings = UserSettingsSerializer(read_only=True)

    phoneNumber = serializers.CharField(source="phone_number")
    verificationStatus = serializers.CharField(
        source="verification_status", read_only=True
    )

    cratedAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = UserModel
        fields = [
            "id",
            "username",
            "email",
            "phoneNumber",
            "role",
            "verificationStatus",
            "updatedAt",
            "cratedAt",
            "profile",
            "settings",
        ]
        read_only_fields = [
            "id",
            "status",
            "role",
            "verificationStatus",
            "is_staff",
            "cratedAt",
            "updatedAt",
            "deleted_at",
            "profile",
            "settings",
        ]
