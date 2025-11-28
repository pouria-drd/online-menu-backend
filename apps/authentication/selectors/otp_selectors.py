import hmac
import hashlib
from django.utils import timezone
from datetime import datetime, timedelta

from apps.authentication.models import OTPModel
from apps.authentication.constants import OTP_EXPIRY_MINUTES, MAX_VERIFY_ATTEMPTS


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
    def is_valid(otp: OTPModel, code: str) -> bool:
        """
        Check if OTP is valid by checking
        1. comparing code with code_hash
        2. checking if OTP is not used
        3. checking if OTP is not expired
        4. checking if remaining attempts is greater than 0
        """
        # Check if code is correct
        hashed_code = OTPSelectors.hash_code(code, otp.salt)
        is_code_correct = hmac.compare_digest(hashed_code, otp.code_hash)

        if not is_code_correct:
            return False

        # Check if OTP is not used, expired, or has remaining attempts
        is_used = OTPSelectors.is_used(otp)
        is_expired = OTPSelectors.is_expired(otp)
        remaining_attempts = OTPSelectors.remaining_attempts(otp)
        # Return True if all conditions are met
        result = not is_used and not is_expired and remaining_attempts > 0
        return result

    @staticmethod
    def hash_code(code: str, salt: str) -> str:
        """
        Return HMAC-SHA256 hex digest of code using salt.
        """
        return hmac.new(salt.encode(), code.encode(), hashlib.sha256).hexdigest()
