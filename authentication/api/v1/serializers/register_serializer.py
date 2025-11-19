from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.core.validators import EmailValidator, RegexValidator

from users.models import UserModel
from authentication.models import OTPModel
from authentication.utils import send_otp_email
from authentication.constants import (
    OTP_EXPIRY_MINUTES,
    OTP_LENGTH,
    OTPType,
)


# -----------------------------
# Reusable validation mixin
# -----------------------------
class UniqueUsernameEmailMixin:
    def validate_username(self, value):
        """Validate username uniqueness (case-insensitive)."""
        username = value.strip().lower()
        if UserModel.objects.filter(username__iexact=username).exists():
            raise ValidationError(
                detail="A user with this username already exists.",
                code="username_taken",
            )
        return username

    def validate_email(self, value):
        """Validate email uniqueness (case-insensitive)."""
        email = value.strip().lower()
        if UserModel.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                detail="A user with this email already exists.", code="email_taken"
            )
        return email


# -----------------------------
# Step 1: Send OTP
# -----------------------------
class RegisterStep1Serializer(serializers.Serializer, UniqueUsernameEmailMixin):
    """
    Step 1 of registration: validate email & username, generate and send OTP.
    """

    email = serializers.EmailField(
        required=True,
        validators=[
            EmailValidator(code="invalid_email", message="Enter a valid email address.")
        ],
        error_messages={
            "required": "Email is required",
            "blank": "Email cannot be blank",
        },
    )

    username = serializers.CharField(
        required=True,
        min_length=3,
        max_length=25,
        validators=[
            RegexValidator(
                regex=r"^[a-z][a-z0-9_]{2,24}$",
                message="Username must start with a letter and contain only lowercase letters, numbers, and underscores.",
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

    @transaction.atomic
    def send_otp(self, validated_data):
        """
        Generate and send OTP for registration.
        Returns OTP instance and message.
        """
        email = validated_data["email"]

        # Check for recent OTP (rate limit)
        recent_otp = (
            OTPModel.objects.filter(
                email=email, otp_type=OTPType.REGISTER, is_used=False
            )
            .order_by("-created_at")
            .first()
        )

        if (
            recent_otp
            and not recent_otp.expired
            and (timezone.now() - recent_otp.created_at).total_seconds()
            < 60 * OTP_EXPIRY_MINUTES
        ):
            raise ValidationError(
                detail=f"You can request a new OTP after {OTP_EXPIRY_MINUTES} minutes.",
                code="otp_rate_limited",
            )

        # Generate OTP
        otp_instance, otp_code = OTPModel.generate_otp(
            email=email, otp_type=OTPType.REGISTER
        )

        # Send OTP via email
        send_otp_email(email, otp_code)

        return {
            "email": email,
            "otp_instance": otp_instance,
            "message": "OTP sent successfully.",
        }


# -----------------------------
# Step 2: Verify OTP and create user
# -----------------------------
class RegisterStep2Serializer(serializers.Serializer, UniqueUsernameEmailMixin):
    """
    Step 2 of registration: validate OTP, mark OTP used, create/verify user.
    """

    email = serializers.EmailField(
        required=True,
        validators=[
            EmailValidator(code="invalid_email", message="Enter a valid email address.")
        ],
        error_messages={
            "required": "Email is required",
            "blank": "Email cannot be blank",
        },
    )

    username = serializers.CharField(
        required=True,
        min_length=3,
        max_length=25,
        validators=[
            RegexValidator(
                regex=r"^[a-z][a-z0-9_]{2,24}$",
                message="Username must start with a letter and contain only lowercase letters, numbers, and underscores.",
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

    code = serializers.CharField(
        required=True,
        min_length=OTP_LENGTH,
        max_length=OTP_LENGTH,
        error_messages={
            "required": "OTP code is required.",
            "blank": "OTP code cannot be blank.",
            "min_length": f"OTP code must be {OTP_LENGTH} characters.",
            "max_length": f"OTP code must be {OTP_LENGTH} characters.",
        },
    )

    def validate(self, attrs):
        email = attrs.get("email")
        code = attrs.get("code")

        # Lookup latest unused OTP
        otp = (
            OTPModel.objects.filter(
                email=email, is_used=False, otp_type=OTPType.REGISTER
            )
            .order_by("-created_at")
            .first()
        )

        if otp is None or otp.expired or not otp.check_code(code):
            raise ValidationError(
                detail={"code": "Invalid or expired OTP code."},
                code="invalid_or_expired_otp_code",
            )

        attrs["otp_instance"] = otp
        return attrs

    @transaction.atomic
    def verify(self, **kwargs):
        """
        Mark OTP as used, create user if not exists, mark email verified.
        Returns info about verification and user creation.
        """
        otp_instance = self.validated_data["otp_instance"]  # type: ignore
        otp_instance.mark_used()

        email = self.validated_data["email"]  # type: ignore
        username = self.validated_data["username"]  # type: ignore

        # Create user
        new_user = UserModel.objects.create_user(  # type: ignore
            email=email, username=username, email_verified=True
        )

        token = new_user.generate_jwt_token()  # type: ignore
        refresh_token = str(token)
        access_token = str(token.access_token)

        return {
            "verified": True,
            "new_user": new_user,
            "access": access_token,
            "refresh": refresh_token,
        }


class RegisterStep3Serializer(serializers.Serializer):
    """
    Step 3 of registration: update user's first and last name.
    """

    first_name = serializers.CharField(
        required=True,
        min_length=2,
        max_length=50,
        error_messages={
            "required": "First name is required",
            "blank": "First name cannot be blank",
            "min_length": "First name must be at least 2 characters",
            "max_length": "First name must be at most 50 characters",
        },
    )

    last_name = serializers.CharField(
        required=True,
        min_length=2,
        max_length=50,
        error_messages={
            "required": "Last name is required",
            "blank": "Last name cannot be blank",
            "min_length": "Last name must be at least 2 characters",
            "max_length": "Last name must be at most 50 characters",
        },
    )

    @transaction.atomic
    def save(self, **kwargs):
        """
        Update user's first name and last name.
        Returns updated user info.
        """
        user = self.context["user"]
        first_name = self.validated_data["first_name"]  # type: ignore
        last_name = self.validated_data["last_name"]  # type: ignore

        user_profile = user.profile
        user_profile.first_name = first_name
        user_profile.last_name = last_name

        user_profile.save(update_fields=["first_name", "last_name"])

        return {
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }


class RegisterStep4Serializer(serializers.Serializer):
    """
    Step 4 of registration: update user's password.
    """

    password = serializers.CharField(
        required=True,
        write_only=True,
        style={"input_type": "password"},
        error_messages={
            "required": "Password is required",
            "blank": "Password cannot be blank",
        },
    )

    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        style={"input_type": "password"},
        error_messages={
            "required": "Confirm password is required",
            "blank": "Confirm password cannot be blank",
        },
    )

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        if password != confirm_password:
            raise ValidationError(
                detail={"confirm_password": "Passwords do not match."},
                code="passwords_do_not_match",
            )

        return attrs

    @transaction.atomic
    def save(self, **kwargs):
        """
        Update user's password.
        Returns updated user info.
        """
        user = self.context["user"]
        password = self.validated_data["password"]  # type: ignore

        user.set_password(password)
        user.save()

        return {
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
