from rest_framework import serializers
from django.contrib.auth import authenticate


class LoginSerializer(serializers.Serializer):
    """
    Serializer for authenticating a user.
    """

    username = serializers.CharField(
        min_length=3,
        max_length=25,
        error_messages={
            "required": "username is required",
            "blank": "username cannot be blank",
            "min_length": "username must be at least 3 characters",
            "max_length": "username must be at most 25 characters",
        },
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        error_messages={
            "required": "password is required",
            "blank": "password cannot be blank",
        },
    )

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        # Authenticate the user
        user = authenticate(username=username, password=password)
        if user is None or not user.is_active:
            raise serializers.ValidationError(
                {
                    "code": "invalid_credentials",
                    "detail": "Invalid username or password.",
                }
            )
        data["user"] = user
        return data
