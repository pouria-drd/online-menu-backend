import hmac
import random
import secrets
from django.db import transaction
from rest_framework.exceptions import ValidationError

from core.constants import OTP_LENGTH, OTPType
from authentication.models import OTPModel
from authentication.selectors import OTPSelectors
from authentication.repositories import OTPRepository


class OTPService:
    @staticmethod
    @transaction.atomic
    def generate(email: str, otp_type: OTPType = OTPType.LOGIN) -> OTPModel:
        """
        Generate new OTP and return (otp_model, plain_code).
        Ensures old/expired otps are cleared and only one active exists.
        """
        OTPRepository.delete_expired_otp(email)

        active_otp = OTPRepository.get_active_otp(email, otp_type)
        if active_otp and not OTPSelectors.is_expired(active_otp):
            raise ValidationError(
                {
                    "form": "An active OTP already exists. Please wait before requesting a new one."
                },
                code="otp_exists",
            )

        salt = secrets.token_hex(16)
        code = f"{random.randint(0, 10**OTP_LENGTH - 1):0{OTP_LENGTH}d}"

        code_hash = OTPSelectors.hash_code(code, salt)

        otp = OTPRepository.create_otp(
            email=email, otp_type=otp_type, salt=salt, code_hash=code_hash
        )

        # TODO: Send code to user via email service
        print("============ OTP Code =============")
        print(f"Email: {otp.email}")
        print(f"Code:  {code}")
        print("====================================\n")

        return otp

    @staticmethod
    @transaction.atomic
    def verify(email: str, code: str) -> bool:
        """
        Verify code, increment attempts, mark used if valid.
        Returns True on success, False otherwise.
        """
        # Get active OTP
        active_otp = OTPRepository.get_active_otp(email, OTPType.LOGIN)
        if not active_otp:
            return False

        # Increment attempts
        OTPRepository.increment_attempts(active_otp)

        # Check if OTP is valid
        is_valid_otp = OTPSelectors.is_valid(active_otp, code)
        if is_valid_otp:
            # Mark OTP as used
            OTPRepository.mark_used(active_otp)
            return True

        return False
