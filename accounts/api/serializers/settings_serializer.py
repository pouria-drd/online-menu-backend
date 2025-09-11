from rest_framework import serializers
from accounts.models import SettingsModel


class SettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for user-specific settings.
    Handles validation for enabling/disabling email 2FA,
    and exposes read-only metadata fields.
    """

    email2fa = serializers.BooleanField(
        source="email_2fa",
        error_messages={
            "invalid": "2FA can only be enabled if the email is verified.",
        },
    )
    emailVerified = serializers.BooleanField(source="email_verified", read_only=True)

    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = SettingsModel
        fields = [
            "id",
            "theme",
            "language",
            "email2fa",
            "emailVerified",
            "updatedAt",
            "createdAt",
        ]
        read_only_fields = [
            "id",
            "user",
            "updatedAt",
            "createdAt",
        ]
        extra_kwargs = {
            "theme": {"required": False},
            "language": {"required": False},
        }

    def validate(self, attrs: dict) -> dict:
        """
        Custom validation to ensure 2FA can only be enabled if
        the user's email has been verified.
        """
        email_2fa = attrs.get("email_2fa")
        if email_2fa and self.instance and not self.instance.can_enable_2fa():
            raise serializers.ValidationError(
                {"email2fa": "2FA can only be enabled if the email is verified."},
                code="invalid_email_2fa",
            )
        return attrs
