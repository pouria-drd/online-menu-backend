from rest_framework import serializers
from accounts.models import UserSettings
from accounts.constants import UserVerificationStatus


class UserSettingsSerializer(serializers.ModelSerializer):
    emailOtpLogin = serializers.BooleanField(source="email_otp_login")
    phoneOtpLogin = serializers.BooleanField(source="phone_otp_login")

    updatedAt = serializers.DateTimeField(read_only=True, source="updated_at")
    createdAt = serializers.DateTimeField(read_only=True, source="created_at")

    class Meta:
        model = UserSettings
        fields = [
            "id",
            "theme",
            "language",
            "emailOtpLogin",
            "phoneOtpLogin",
            "updatedAt",
            "createdAt",
        ]
        read_only_fields = [
            "id",
            "user",
            "updatedAt",
            "createdAt",
        ]

    def validate(self, attrs):
        user = getattr(self.instance, "user", None)
        if not user:
            raise serializers.ValidationError("User instance is required.")

        if (
            attrs.get("email_otp_login") or attrs.get("phone_otp_login")
        ) and user.verification_status != UserVerificationStatus.VERIFIED:
            raise serializers.ValidationError(
                "OTP login can only be enabled for verified users."
            )
        return attrs

    def update(self, instance, validated_data):
        # Partial update
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
