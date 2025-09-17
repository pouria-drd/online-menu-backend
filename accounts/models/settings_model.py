import uuid
from typing import List
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from accounts.constants import UserLanguage, UserTheme, TwoFactorMethod

User = get_user_model()


class SettingsModel(models.Model):
    """
    Model for storing user settings including 2FA configuration
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # One-to-one relationship with UserModel
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="settings")

    # Theme & Appearance
    theme = models.CharField(
        max_length=10, choices=UserTheme.choices, default=UserTheme.SYSTEM
    )
    language = models.CharField(
        max_length=20, choices=UserLanguage.choices, default=UserLanguage.PERSIAN
    )
    # 2FA Configuration - More flexible approach
    primary_2fa_method = models.CharField(
        max_length=20,
        choices=TwoFactorMethod.choices,
        blank=True,
        null=True,
        help_text="Primary 2FA method for this user",
    )

    # Individual 2FA method enablement
    email_2fa_enabled = models.BooleanField(
        default=False, help_text="Email-based 2FA is enabled"
    )
    # Future: Add SMS, TOTP fields here

    # Verification status
    email_verified = models.BooleanField(default=False)
    # Future: Add phone_verified field here

    # Security settings
    require_2fa_for_sensitive_actions = models.BooleanField(
        default=False,
        help_text="Require 2FA for password changes, account deletion, etc.",
    )

    # Date & Time
    last_2fa_setup_at = models.DateTimeField(
        null=True, blank=True, help_text="When 2FA was last configured"
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s settings"

    class Meta:
        verbose_name = "User Setting"
        verbose_name_plural = "User Settings"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["primary_2fa_method"]),
        ]

    def clean(self):
        """Validate 2FA configuration"""
        errors = {}

        # Check if email 2FA is enabled but prerequisites aren't met
        if self.email_2fa_enabled and not self.email_verified:
            errors["email_2fa_enabled"] = ValidationError(
                "Email 2FA requires verified email address"
            )

        # Validate primary method is actually enabled
        if self.primary_2fa_method and not self.is_2fa_method_enabled(
            self.primary_2fa_method
        ):
            errors["primary_2fa_method"] = ValidationError(
                "Primary 2FA method must be enabled"
            )

        # If any 2FA is enabled, ensure primary method is set
        if self.has_any_2fa_enabled() and not self.primary_2fa_method:
            errors["primary_2fa_method"] = ValidationError(
                "Primary 2FA method must be selected when 2FA is enabled"
            )

        if errors:
            raise ValidationError(errors)

    # 2FA Status Methods
    def has_any_2fa_enabled(self) -> bool:
        """Check if any 2FA method is enabled"""
        return self.email_2fa_enabled

    def get_enabled_2fa_methods(self) -> List[str]:
        """Get list of all enabled 2FA methods"""
        methods = []
        if self.email_2fa_enabled:
            methods.append(TwoFactorMethod.EMAIL)
        # Future: Add other methods here
        return methods

    def is_2fa_method_enabled(self, method: str) -> bool:
        """Check if specific 2FA method is enabled"""
        method_map = {
            TwoFactorMethod.EMAIL: self.email_2fa_enabled,
            # Future: Add other methods here
        }
        return method_map.get(method, False)  # type: ignore

    # 2FA Management Methods
    def can_enable_2fa_method(self, method: str) -> tuple[bool, str]:
        """
        Check if user can enable specific 2FA method
        Returns (can_enable, reason_if_not)
        """
        if method == TwoFactorMethod.EMAIL:
            if not self.email_verified:
                return False, "Email must be verified first"
        else:
            return False, "Unknown 2FA method"

        return True, ""

    def enable_2fa_method(self, method: str, set_as_primary: bool = True) -> bool:
        """
        Enable specific 2FA method
        Returns True if successful, raises ValidationError if not
        """
        can_enable, reason = self.can_enable_2fa_method(method)
        if not can_enable:
            raise ValidationError(f"Cannot enable {method} 2FA: {reason}")

        # Enable the method
        if method == TwoFactorMethod.EMAIL:
            self.email_2fa_enabled = True
        else:
            raise ValueError(f"Unknown 2FA method: {method}")

        # Set as primary if requested and no primary exists
        if set_as_primary or not self.primary_2fa_method:
            self.primary_2fa_method = method

        from django.utils import timezone

        self.last_2fa_setup_at = timezone.now()

        self.save(
            update_fields=[
                f"{method}_2fa_enabled",
                "primary_2fa_method",
                "last_2fa_setup_at",
            ]
        )
        return True

    def disable_2fa_method(self, method: str) -> bool:
        """Disable specific 2FA method"""
        if not self.is_2fa_method_enabled(method):
            return False

        # Disable the method
        if method == TwoFactorMethod.EMAIL:
            self.email_2fa_enabled = False
        else:
            raise ValueError(f"Unknown 2FA method: {method}")

        # Update primary method if we just disabled it
        update_fields = [f"{method}_2fa_enabled"]
        if self.primary_2fa_method == method:
            enabled_methods = self.get_enabled_2fa_methods()
            if enabled_methods:
                # Set first available method as primary
                self.primary_2fa_method = enabled_methods[0]
            else:
                # No 2FA methods left
                self.primary_2fa_method = None
            update_fields.append("primary_2fa_method")

        self.save(update_fields=update_fields)
        return True

    def disable_all_2fa(self):
        """Disable all 2FA methods"""
        self.email_2fa_enabled = False
        self.primary_2fa_method = None

        self.save(
            update_fields=[
                "email_2fa_enabled",
                "primary_2fa_method",
            ]
        )

    # Legacy compatibility method
    def set_2fa(self, method: str, value: bool):
        """
        Legacy method for backwards compatibility
        Consider using enable_2fa_method/disable_2fa_method instead
        """
        if value:
            self.enable_2fa_method(method)
        else:
            self.disable_2fa_method(method)
