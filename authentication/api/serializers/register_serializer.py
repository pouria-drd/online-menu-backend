from rest_framework import serializers
from accounts.constants import UserRole
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from django.core.validators import EmailValidator, RegexValidator
from django.contrib.auth.password_validation import validate_password

UserModel = get_user_model()


class RegisterSerializer(serializers.Serializer):

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
                code="invalid_username",
                message="Username must start with a letter and contain only lowercase letters, numbers, and underscores.",
            )
        ],
    )

    role = serializers.ChoiceField(
        default=UserRole.USER,
        choices=[UserRole.USER, UserRole.MENU_OWNER],
        error_messages={
            "invalid_choice": "Role must be either 'user' or 'menu_owner'."
        },
    )

    lastName = serializers.CharField(
        min_length=3,
        max_length=50,
        required=False,
        error_messages={
            "min_length": "Last name must be at least 3 characters",
            "max_length": "Last name must be at most 50 characters",
        },
    )

    firstName = serializers.CharField(
        min_length=2,
        max_length=50,
        required=False,
        error_messages={
            "min_length": "First name must be at least 2 characters",
            "max_length": "First name must be at most 50 characters",
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
    confirmPassword = serializers.CharField(
        required=True,
        write_only=True,
        error_messages={
            "required": "Confirm password is required",
            "blank": "Confirm password cannot be blank",
        },
    )

    def validate_username(self, value):
        if UserModel.objects.filter(username=value).exists():
            raise ValidationError("Username already exists.")
        return value

    def validate_email(self, value):
        if UserModel.objects.filter(email=value).exists():
            raise ValidationError("Email already exists.")
        return value.lower()

    def validate(self, data):
        # Password confirmation check
        if data["password"] != data["confirmPassword"]:
            raise ValidationError(
                {"confirmPassword": "Password and confirm password must match."}
            )
        validate_password(data["password"])
        return data

    def create(self, validated_data):
        validated_data.pop("confirmPassword", None)
        first_name = validated_data.pop("firstName", "")
        last_name = validated_data.pop("lastName", "")

        user = UserModel.objects.create_user(  # type: ignore
            **validated_data,
        )

        if first_name or last_name:
            user.profile.first_name = first_name  # type: ignore
            user.profile.last_name = last_name  # type: ignore
            user.profile.save()  # type: ignore

        return user
