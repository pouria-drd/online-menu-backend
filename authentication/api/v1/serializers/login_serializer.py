from rest_framework import serializers
from django.core.validators import EmailValidator

from core.constants import OTP_LENGTH


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


class VerifyLoginOTPSerializer(serializers.Serializer):
    """
    Serializer for verifying a user via OTP.
    """

    email = serializers.EmailField(
        required=True,
        validators=[EmailValidator],
        error_messages={
            "required": "Email is required",
            "blank": "Email cannot be blank",
        },
    )

    code = serializers.CharField(
        required=True,
        write_only=True,
        min_length=OTP_LENGTH,
        max_length=OTP_LENGTH,
        style={"input_type": "password"},
        error_messages={
            "required": "Code is required",
            "blank": "Code cannot be blank",
            "min_length": f"Code must be at least {OTP_LENGTH} characters long.",
            "max_length": f"Code must be at most {OTP_LENGTH} characters long.",
        },
    )
