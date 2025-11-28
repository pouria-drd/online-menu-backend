from rest_framework import serializers
from django.core.validators import EmailValidator


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
