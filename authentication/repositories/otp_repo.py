import hmac
import hashlib

from datetime import timedelta
from django.utils import timezone
from django.db.models import F, Q
from authentication.models import OTPModel
from core.constants import OTP_EXPIRY_MINUTES


class OTPRepository:
    """Repository layer for OTP-related DB operations."""

    @staticmethod
    def create(email: str, otp_type: str, salt: str, code_hash: str):
        """Create new OTP for email."""
        return OTPModel.objects.create(
            email=email, otp_type=otp_type, salt=salt, code_hash=code_hash
        )

    @staticmethod
    def delete_expired_or_used(email: str):
        """Delete expired or used OTPs for email."""
        OTPModel.objects.filter(email=email).filter(
            Q(is_used=True)
            | Q(created_at__lt=timezone.now() - timedelta(minutes=OTP_EXPIRY_MINUTES))
        ).delete()

    @staticmethod
    def get_active(email: str, otp_type):
        """Get active OTP for email and otp_type."""
        return OTPModel.objects.filter(
            email=email, otp_type=otp_type, is_used=False
        ).first()

    @staticmethod
    def increment_attempts(otp: OTPModel):
        """Increment attempts by 1 for OTP."""
        OTPModel.objects.filter(pk=otp.pk).update(attempts=F("attempts") + 1)
        otp.refresh_from_db(fields=["attempts"])

    @staticmethod
    def mark_used(otp: OTPModel):
        """Mark OTP as used."""
        if not otp.is_used:
            otp.is_used = True
            otp.save(update_fields=["is_used"])

    @staticmethod
    def hash_code(code: str, salt: str) -> str:
        """
        Return HMAC-SHA256 hex digest of code using salt.
        """
        return hmac.new(salt.encode(), code.encode(), hashlib.sha256).hexdigest()
