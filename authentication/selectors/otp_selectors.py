from datetime import timedelta
from django.utils import timezone

from authentication.models import OTPModel
from core.constants import OTP_EXPIRY_MINUTES, MAX_VERIFY_ATTEMPTS


class OTPSelectors:
    """Selector class for OTP-related properties."""

    @staticmethod
    def is_expired(otp: OTPModel) -> bool:
        return timezone.now() > otp.created_at + timedelta(minutes=OTP_EXPIRY_MINUTES)

    @staticmethod
    def is_used(otp: OTPModel) -> bool:
        return otp.is_used

    @staticmethod
    def remaining_attempts(otp: OTPModel) -> int:
        return max(0, MAX_VERIFY_ATTEMPTS - otp.attempts)

    @staticmethod
    def is_valid(otp: OTPModel) -> bool:
        return (
            not OTPSelectors.is_used(otp)
            and not OTPSelectors.is_expired(otp)
            and OTPSelectors.remaining_attempts(otp) > 0
        )
