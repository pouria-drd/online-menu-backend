import hmac
import uuid
from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model

from authentication.utils import generate_otp_code, hash_otp
from authentication.constants import OTP_EXPIRY_MINUTES, UseCase

User = get_user_model()


class OTPModel(models.Model):
    """OTP Model for storing OTP codes and validations."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otps")
    usecase = models.CharField(
        max_length=20, choices=UseCase.choices, default=UseCase.EMAIL_2FA
    )
    # Store hashed OTP
    code_hash = models.CharField(max_length=256)
    # Number of verification attempts
    attempts = models.PositiveIntegerField(default=0)
    # Max allowed attempts
    max_attempts = models.PositiveIntegerField(default=3)
    # Is OTP code used
    used = models.BooleanField(default=False)
    # Timestamps
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_attempted = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "OTP code"
        verbose_name_plural = "OTP codes"
        indexes = [
            models.Index(fields=["user", "usecase"]),
            models.Index(fields=["expires_at"]),
        ]

    @property
    def is_expired(self) -> bool:
        """Check if the OTP has expired."""
        return timezone.now() > self.expires_at

    @property
    def can_attempt(self) -> bool:
        """Check if the OTP has attempts left."""
        return self.attempts < self.max_attempts and not self.is_expired

    def check_otp(self, otp_code) -> bool:
        """Compare the OTP code with the stored OTP code."""
        return hmac.compare_digest(self.code_hash, hash_otp(otp_code))

    def mark_used(self):
        """Mark the OTP code as used."""
        self.used = True
        self.save(update_fields=["used"])

    def increment_attempts(self):
        """Increment the number of attempts."""
        self.attempts += 1
        # self.last_attempted = timezone.now()
        self.save(update_fields=["attempts", "last_attempted"])

    def validate(self, otp_code: str) -> bool:
        """Validate the OTP code."""
        if self.used or self.is_expired or not self.can_attempt:
            return False
        if not self.check_otp(otp_code):
            self.increment_attempts()
            return False
        self.mark_used()
        return True

    @classmethod
    def create_otp(cls, user, usecase: UseCase = UseCase.EMAIL_2FA, length: int = 5):
        """Create a new OTP code."""
        # Generate OTP code and hash it
        otp_code = generate_otp_code(length)
        code_hash = hash_otp(otp_code)
        # Create OTP object
        otp_obj = cls.objects.create(
            user=user,
            usecase=usecase,
            code_hash=code_hash,
            expires_at=timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES),
        )
        # Return OTP code and OTP object
        return otp_code, otp_obj
