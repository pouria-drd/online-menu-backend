from rest_framework import serializers
from django.contrib.auth import authenticate


class LoginSerializer(serializers.Serializer):
    """
    Serializer for authenticating a user.
    """

    username = serializers.CharField(
        min_length=3,
        max_length=100,
        error_messages={
            "required": "Username or email is required",
            "blank": "Username or email cannot be blank",
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

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        # Authenticate the user
        user = authenticate(username=username, password=password)
        if user is None or not user.is_active:
            raise serializers.ValidationError(
                {"username": "Invalid username or password."},
                code="invalid_credentials",
            )
        data["user"] = user
        return data
