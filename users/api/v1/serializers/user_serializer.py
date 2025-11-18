from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.core.validators import EmailValidator, RegexValidator
from django.contrib.auth.password_validation import validate_password


from .profile_serializer import ProfileSerializer
from .settings_serializer import SettingsSerializer
from users.models import UserModel, ProfileModel, SettingsModel


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[
            EmailValidator(
                code="invalid_email",
                message="Enter a valid email address.",
            )
        ],
        error_messages={
            "required": "Email is required",
            "blank": "Email cannot be blank",
        },
    )

    username = serializers.CharField(
        min_length=3,
        max_length=25,
        validators=[
            RegexValidator(
                regex=r"^[a-z][a-z0-9_]{2,24}$",
                message=(
                    "Username must start with a letter and contain only lowercase "
                    "letters, numbers, and underscores."
                ),
                code="invalid_username",
            )
        ],
        error_messages={
            "required": "Username is required.",
            "blank": "Username cannot be blank.",
            "min_length": "Username must be at least 3 characters.",
            "max_length": "Username cannot exceed 25 characters.",
        },
    )

    password = serializers.CharField(
        required=True,
        write_only=True,
        error_messages={
            "required": "Password is required",
            "blank": "Password cannot be blank",
        },
    )
    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        error_messages={
            "required": "Confirm password is required",
            "blank": "Confirm password cannot be blank",
        },
    )

    updatedAt = serializers.DateTimeField(read_only=True, source="updated_at")
    createdAt = serializers.DateTimeField(read_only=True, source="created_at")

    profile = ProfileSerializer(required=False, allow_null=True)
    settings = SettingsSerializer(required=False, allow_null=True)

    class Meta:
        model = UserModel
        fields = [
            "id",
            "username",
            "email",
            "role",
            "status",
            "password",
            "confirm_password",
            "profile",
            "settings",
            "updatedAt",
            "createdAt",
        ]
        read_only_fields = ["id", "status", "role", "created_at", "updated_at"]

    def validate_username(self, value):
        user = self.instance
        if (
            UserModel.objects.filter(username=value)
            .exclude(pk=getattr(user, "pk", None))
            .exists()
        ):
            raise ValidationError("Username already exists.")
        return value

    def validate_email(self, value):
        user = self.instance
        if (
            UserModel.objects.filter(email=value)
            .exclude(pk=getattr(user, "pk", None))
            .exists()
        ):
            raise ValidationError("Email already exists.")
        return value.lower()

    def validate(self, data):
        if "password" in data and "confirm_password" in data:
            if data["password"] != data["confirm_password"]:
                raise ValidationError(
                    {"confirm_password": "Password and confirm password must match."}
                )
            validate_password(data["password"])
        return data

    def create(self, validated_data):
        profile_data = validated_data.pop("profile", None)
        settings_data = validated_data.pop("settings", None)

        validated_data.pop("confirm_password", None)
        password = validated_data.pop("password", None)

        user = UserModel.objects.create_user(**validated_data)  # type: ignore
        if password:
            user.set_password(password)
            user.save()

        # Create related profile
        if profile_data:
            ProfileModel.objects.update_or_create(user=user, defaults=profile_data)

        # Create related settings
        if settings_data:
            SettingsModel.objects.update_or_create(user=user, defaults=settings_data)

        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", None)
        settings_data = validated_data.pop("settings", None)

        validated_data.pop("confirm_password", None)
        password = validated_data.pop("password", None)

        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        # Update or create profile
        if profile_data:
            ProfileModel.objects.update_or_create(user=instance, defaults=profile_data)

        # Update or create settings
        if settings_data:
            SettingsModel.objects.update_or_create(
                user=instance, defaults=settings_data
            )

        return instance
