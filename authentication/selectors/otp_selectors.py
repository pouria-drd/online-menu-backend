from django.utils import timezone
from datetime import datetime, timedelta

from authentication.models import OTPModel
from core.constants import OTP_EXPIRY_MINUTES, MAX_VERIFY_ATTEMPTS


class OTPSelectors:
    """Selector class for OTP-related properties."""

    @staticmethod
    def is_expired(otp: OTPModel) -> bool:
        """Check if OTP is expired by comparing current time with expire_at."""
        now = timezone.now()
        expire_at = OTPSelectors.expire_at(otp)
        result = now > expire_at
        return result

    @staticmethod
    def expire_at(otp: OTPModel) -> datetime:
        """Return datetime object for expiry of OTP."""
        result = otp.created_at + timedelta(minutes=OTP_EXPIRY_MINUTES)
        return result

    @staticmethod
    def is_used(otp: OTPModel) -> bool:
        """Check if OTP is used."""
        return otp.is_used

    @staticmethod
    def remaining_attempts(otp: OTPModel) -> int:
        """Return remaining attempts for OTP."""
        return max(0, MAX_VERIFY_ATTEMPTS - otp.attempts)

    @staticmethod
    def is_valid(otp: OTPModel) -> bool:
        """Check if OTP is valid by checking if it's not used, not expired, and has remaining attempts."""
        return (
            not OTPSelectors.is_used(otp)
            and not OTPSelectors.is_expired(otp)
            and OTPSelectors.remaining_attempts(otp) > 0
        )
