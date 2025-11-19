from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import EmailValidator
from rest_framework.exceptions import ValidationError

from authentication.models import OTPModel
from authentication.utils import send_otp_email
from authentication.constants import (
    OTP_EXPIRY_MINUTES,
    OTP_LENGTH,
    OTPType,
)

UserModel = get_user_model()


class SendOTPLoginSerializer(serializers.Serializer):
    """
    Step 1 of otp login: validate email & username, generate and send OTP.
    """

    email = serializers.EmailField(
        required=True,
        validators=[EmailValidator],
        error_messages={
            "required": "Email is required",
            "blank": "Email cannot be blank",
        },
    )

    def validate_email(self, value):
        """Check if email is associated with any user account."""
        email = value.strip().lower()
        if UserModel.objects.filter(email=email).exists():
            return email
        else:
            raise ValidationError(
                detail="There are no user accounts associated with this email address.",
                code="user_not_found",
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
            OTPModel.objects.filter(email=email, otp_type=OTPType.LOGIN, is_used=False)
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
                detail=f"You can request a new OTP every {OTP_EXPIRY_MINUTES} minutes.",
                code="otp_rate_limited",
            )

        # Generate OTP
        otp_instance, otp_code = OTPModel.generate_otp(
            email=email, otp_type=OTPType.LOGIN
        )

        # Send OTP via email
        send_otp_email(email, otp_code)

        return {
            "email": email,
            "otp_instance": otp_instance,
            "message": "OTP sent successfully.",
        }


class VerifyOTPLoginSerializer(serializers.Serializer):
    """
    Step 2 of otp login: validate OTP, mark OTP used, login user.
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
            OTPModel.objects.filter(email=email, is_used=False, otp_type=OTPType.LOGIN)
            .order_by("-created_at")
            .first()
        )
        # Validate OTP
        if otp is None or otp.expired or not otp.check_code(code):
            raise ValidationError(
                detail={"code": "Invalid or expired OTP code."},
                code="invalid_or_expired_otp_code",
            )
        # Check if user exists and is active
        user = UserModel.objects.get(email=email)
        if user is None or not user.is_active or not user.email_verified:  # type: ignore
            raise serializers.ValidationError(
                {"form": "Invalid credentials"},
                code="invalid_credentials",
            )
        # Add user and otp to validated data
        attrs["user"] = user
        attrs["otp_instance"] = otp

        return attrs

    @transaction.atomic
    def verify(self, **kwargs):
        """
        Mark OTP as used and generate JWT tokens.
        """
        otp_instance = self.validated_data["otp_instance"]  # type: ignore
        otp_instance.mark_used()

        user = self.validated_data["user"]  # type: ignore

        # Generate JWT tokens
        token = user.generate_jwt_token()  # type: ignore
        refresh_token = str(token)
        access_token = str(token.access_token)

        return {
            "access": access_token,
            "refresh": refresh_token,
        }
