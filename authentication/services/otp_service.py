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
        OTPRepository.delete_expired_or_used(email)

        active = OTPRepository.get_active(email, otp_type)
        if active and not OTPSelectors.is_expired(active):
            raise ValidationError(
                {
                    "form": "An active OTP already exists. Please wait before requesting a new one."
                },
                code="otp_exists",
            )

        salt = secrets.token_hex(16)
        code = f"{random.randint(0, 10**OTP_LENGTH - 1):0{OTP_LENGTH}d}"

        code_hash = OTPRepository.hash_code(code, salt)

        otp = OTPRepository.create(
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
        otp = OTPRepository.get_active(email, OTPType.LOGIN)

        if not otp:
            return False

        if not OTPSelectors.is_valid(otp):
            return False

        OTPRepository.increment_attempts(otp)

        valid = hmac.compare_digest(
            OTPRepository.hash_code(code, otp.salt), otp.code_hash
        )

        if valid:
            OTPRepository.mark_used(otp)

        return valid
