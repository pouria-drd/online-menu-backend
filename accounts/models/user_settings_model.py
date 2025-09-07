import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from accounts.constants import UserLanguage, UserTheme, UserVerificationStatus


User = get_user_model()


class UserSettings(models.Model):
    """
    Model for storing user settings
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # One-to-one relationship with UserModel
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="settings")
    # Theme & Appearance
    theme = models.CharField(
        max_length=10, choices=UserTheme.choices, default=UserTheme.SYSTEM
    )
    # Security
    email_otp_login = models.BooleanField(
        default=False,
        help_text="Allow login using email OTP if user is fully verified.",
    )
    phone_otp_login = models.BooleanField(
        default=False,
        help_text="Allow login using phone OTP if user is fully verified.",
    )
    # Localization
    language = models.CharField(
        max_length=20, choices=UserLanguage.choices, default=UserLanguage.PERSIAN
    )
    # Date & Time
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s settings"

    class Meta:
        verbose_name = "User Setting"
        verbose_name_plural = "User Settings"
        indexes = [
            models.Index(fields=["user"]),
        ]

    def clean(self):
        if (self.email_otp_login or self.phone_otp_login) and not self.can_enable_otp():
            raise ValidationError("OTP login can only be enabled for verified users.")

    def can_enable_otp(self) -> bool:
        """Check if user can enable OTP login"""
        return self.user.verification_status == UserVerificationStatus.VERIFIED  # type: ignore

    def set_otp(self, method: str, value: bool) -> bool:
        """Enable or disable OTP login method ('email' or 'phone')"""
        if not self.can_enable_otp():
            return False

        if method == "email":
            self.email_otp_login = value
        elif method == "phone":
            self.phone_otp_login = value
        else:
            raise ValueError("Invalid OTP method. Use 'email' or 'phone'.")

        self.save(update_fields=[f"{method}_otp_login"])
        return True
