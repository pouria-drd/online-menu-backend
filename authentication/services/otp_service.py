import hmac
import random
import secrets
from django.db import transaction
from django.core.exceptions import ValidationError

from core.constants import OTP_LENGTH, OTPType, MAX_VERIFY_ATTEMPTS

from authentication.models import OTPModel
from authentication.repositories.otp_repo import OTPRepository
from authentication.selectors.otp_selectors import OTPSelectors


class OTPService:
    @staticmethod
    @transaction.atomic
    def generate_otp(email: str, otp_type: OTPType = OTPType.LOGIN) -> tuple:
        """
        Generate new OTP and return (otp_model, plain_code).
        Ensures old/expired otps are cleared and only one active exists.
        """
        OTPRepository.delete_expired_or_used(email)

        active = OTPRepository.get_active(email, otp_type)
        if active and not OTPSelectors.is_expired(active):
            raise ValidationError(
                "Active OTP exists. Wait before requesting another.", code="otp_exists"
            )

        salt = secrets.token_hex(16)
        code = f"{random.randint(0, 10**OTP_LENGTH - 1):0{OTP_LENGTH}d}"

        code_hash = OTPRepository.hash_code(code, salt)

        otp = OTPRepository.create(
            email=email, otp_type=otp_type, salt=salt, code_hash=code_hash
        )

        return otp, code

    @staticmethod
    @transaction.atomic
    def verify(otp: "OTPModel", code: str) -> bool:
        """
        Verify code, increment attempts, mark used if valid.
        Returns True on success, False otherwise.
        """
        if not OTPSelectors.is_valid(otp):
            return False

        OTPRepository.increment_attempts(otp)

        valid = hmac.compare_digest(
            OTPRepository.hash_code(code, otp.salt), otp.code_hash
        )

        if valid:
            OTPRepository.mark_used(otp)

        return valid
