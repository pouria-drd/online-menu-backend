from rest_framework import serializers
from django.core.validators import EmailValidator

from core.constants import OTP_LENGTH


class SendRegisterOTPSerializer(serializers.Serializer):
    """
    Serializer for registering a user via OTP.
    """

    email = serializers.EmailField(
        required=True,
        validators=[EmailValidator],
        error_messages={
            "required": "Email is required",
            "blank": "Email cannot be blank",
        },
    )
