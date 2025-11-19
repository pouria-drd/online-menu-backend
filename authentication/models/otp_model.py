import uuid
import hmac
import random
import secrets
from datetime import timedelta
from django.db import models
from django.db.models import F, Q
from django.utils import timezone
from django.core.validators import EmailValidator

from authentication.utils import hash_code
from authentication.constants import (
    OTP_LENGTH,
    OTP_EXPIRY_MINUTES,
    MAX_VERIFY_ATTEMPTS,
    OTPType,
)


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

    # === Business Logic ===

    @property
    def expired(self) -> bool:
        return timezone.now() > self.created_at + timedelta(minutes=OTP_EXPIRY_MINUTES)

    @property
    def remaining_attempts(self) -> int:
        return max(0, MAX_VERIFY_ATTEMPTS - self.attempts)

    @property
    def can_verify(self) -> bool:
        return not self.is_used and not self.expired and self.remaining_attempts > 0

    def check_code(self, code: str) -> bool:
        if not self.can_verify:
            return False

        OTPModel.objects.filter(pk=self.pk).update(attempts=F("attempts") + 1)
        self.refresh_from_db(fields=["attempts"])

        valid = hmac.compare_digest(hash_code(code, self.salt), self.code_hash)
        if valid:
            self.mark_used()
        return valid

    def mark_used(self):
        if not self.is_used:
            self.is_used = True
            self.save(update_fields=["is_used"])

    @classmethod
    def generate_otp(
        cls, email: str, otp_type: OTPType = OTPType.LOGIN
    ) -> tuple["OTPModel", str]:
        """
        Create and return an OTP instance and the plain code (for sending).
        """
        # Check if OTP already exists
        cls.objects.filter(email=email).filter(
            Q(is_used=True)
            | Q(created_at__lt=timezone.now() - timedelta(minutes=OTP_EXPIRY_MINUTES))
        ).delete()

        # Prevent duplicates
        active = cls.objects.filter(
            email=email, is_used=False, otp_type=otp_type
        ).first()

        if active and not active.expired:
            raise ValueError(
                "An active OTP already exists. Please wait before requesting a new one."
            )

        # Generate code
        code = f"{random.randint(0, 10**OTP_LENGTH - 1):0{OTP_LENGTH}d}"
        salt = secrets.token_hex(16)
        code_hash = hash_code(code, salt)

        otp = cls.objects.create(
            email=email,
            otp_type=otp_type,
            salt=salt,
            code_hash=code_hash,
        )

        return otp, code
