import uuid
from django.db import models
from django.db.models import Q
from core.constants import OTPType
from django.core.validators import EmailValidator


class OTPModel(models.Model):
    """Secure OTP model supporting email."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(
        null=False,
        blank=False,
        validators=[EmailValidator(message="Enter a valid email address.")],
        help_text="Target email for OTP delivery.",
    )

    otp_type = models.CharField(
        max_length=61,
        choices=OTPType.choices,
        default=OTPType.LOGIN,
        help_text="Purpose of the OTP (login, register, etc.).",
    )

    salt = models.CharField(max_length=255)
    code_hash = models.CharField(max_length=255)

    is_used = models.BooleanField(default=False)
    attempts = models.PositiveSmallIntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "OTP Code"
        verbose_name_plural = "OTP Codes"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["email", "otp_type", "is_used"],
                name="unique_active_otp_per_email_type",
                condition=Q(is_used=False),
            )
        ]

    def __str__(self):
        return f"OTP for {self.email} ({self.otp_type})"
