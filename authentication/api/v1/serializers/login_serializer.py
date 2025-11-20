from rest_framework import serializers
from django.core.validators import EmailValidator
from rest_framework.exceptions import ValidationError

from core.constants import OTPType
from authentication.services import AuthService, OTPService


class LoginSerializer(serializers.Serializer):
    """
    Serializer for authenticating a user.
    """

    email = serializers.EmailField(
        required=True,
        validators=[EmailValidator],
        error_messages={
            "required": "Email is required",
            "blank": "Email cannot be blank",
        },
    )

    password = serializers.CharField(
        required=True,
        write_only=True,
        style={"input_type": "password"},
        error_messages={
            "required": "Password is required",
            "blank": "Password cannot be blank",
        },
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = AuthService.login_user(email=email, password=password)

        except ValidationError:
            raise serializers.ValidationError(
                {"form": "Invalid credentials"},
                code="invalid_credentials",
            )

        token = AuthService.generate_jwt_token(user)
        refresh_token = str(token)
        access_token = str(token.access_token)

        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }


class SendLoginOTPSerializer(serializers.Serializer):
    """
    Serializer for authenticating a user via OTP.
    """

    email = serializers.EmailField(
        required=True,
        validators=[EmailValidator],
        error_messages={
            "required": "Email is required",
            "blank": "Email cannot be blank",
        },
    )

    def validate(self, attrs):
        email = attrs.get("email")

        try:
            OTPService.generate_otp(email=email, otp_type=OTPType.LOGIN)

        except ValidationError:
            raise serializers.ValidationError(
                {"form": "Failed to send OTP. Please try again."},
                code="otp_send_failed",
            )

        return email
