import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from accounts.constants import UserLanguage, UserTheme


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
    email_2fa = models.BooleanField(
        default=False,
        help_text="Allow 2FA for email login",
    )
    # Localization
    language = models.CharField(
        max_length=20, choices=UserLanguage.choices, default=UserLanguage.PERSIAN
    )
    # Boolean fields for user status
    email_verified = models.BooleanField(default=False)
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
        if (self.email_2fa) and not self.can_enable_2fa():
            raise ValidationError("2FA can only be enabled for verified email (.etc)")

    def can_enable_2fa(self) -> bool:
        """Check if user can enable 2FA"""
        return self.email_verified

    def set_2fa(self, method: str, value: bool):
        """Enable or disable 2FA for email"""
        if not self.can_enable_2fa():
            raise ValidationError("2FA can only be enabled for verified email (.etc)")

        if method == "email":
            self.email_2fa = value
        else:
            raise ValueError("Invalid OTP method. Use 'email'.")

        self.save(update_fields=[f"{method}_2fa"])
