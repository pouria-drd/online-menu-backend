import secrets
from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.mailer.tasks import send_email_async
from apps.authentication.models import OTPModel
from apps.authentication.selectors import OTPSelectors
from apps.authentication.repositories import OTPRepository
from apps.authentication.constants import OTP_LENGTH, OTPType, ENV_OTP_EXPIRY_MINUTES


class OTPService:
    """
    Service layer responsible for generating, sending, validating,
    and enforcing rules for OTP codes.

    High-level responsibilities:
    - Enforce OTP cooldown rules (no duplicate active OTPs)
    - Generate secure OTP codes + hashed storage
    - Verify input codes safely (constant-time comparison)
    """

    @staticmethod
    @transaction.atomic
    def send_otp(email: str, otp_type: OTPType) -> OTPModel:
        """
        Generates a new OTP, enforces existing cooldown limits,
        stores the OTP (salt + hashed code), and triggers the sending logic.

        Args:
            email (str): Target email address for OTP.
            otp_type (OTPType): Purpose/type of OTP (REGISTER, LOGIN, etc.)

        Raises:
            ValidationError: If another valid OTP exists and user must wait.

        Returns:
            OTPModel: The newly created OTP database object.
        """

        # 1. Remove expired OTPs to keep DB clean
        OTPRepository.delete_expired_otp(email)

        # 2. Check if a usable OTP already exists
        pending_otp = OTPRepository.get_active_otp(email, otp_type)
        if pending_otp and not OTPSelectors.is_expired(pending_otp):
            raise ValidationError(
                {
                    "form": "An active OTP already exists. Please wait before requesting a new one."
                },
                code="otp_exists",
            )

        # 3. Generate new OTP
        otp_code = f"{secrets.randbelow(10 ** OTP_LENGTH):0{OTP_LENGTH}d}"

        otp_salt = secrets.token_hex(16)
        otp_hash = OTPSelectors.hash_code(otp_code, otp_salt)

        # 4. Save OTP in repository
        otp_instance = OTPRepository.create_otp(
            email=email,
            otp_type=otp_type,
            salt=otp_salt,
            code_hash=otp_hash,
        )

        # print("============ OTP Code =============")
        # print(f"Email: {otp_instance.email}")
        # print(f"Code:  {otp_code}")
        # print("====================================\n")

        # Send single email asynchronously
        send_email_async.delay(
            template_slug="otp-verification",
            recipient_email=otp_instance.email,
            recipient_name=otp_instance.email,
            context={
                "name": otp_instance.email,
                "otp_code": otp_code,
                "expiry_minutes": ENV_OTP_EXPIRY_MINUTES,
                "site_name": "Online Menu",
                "support_email": "support@example.com",
            },
        )  # type: ignore

        return otp_instance

    @staticmethod
    @transaction.atomic
    def verify_otp(email: str, code: str, otp_type: OTPType) -> bool:
        """
        Validates an OTP against the stored hashed code, enforcing
        expiration rules and incrementing attempt counters.

        Args:
            email (str): Email that OTP was sent to.
            code (str): Code provided by the user.
            otp_type (OTPType): The OTP category.

        Returns:
            bool: True if OTP is correct and successfully validated, else False.
        """

        # 1. Retrieve the pending OTP
        pending_otp = OTPRepository.get_active_otp(email, otp_type)
        if not pending_otp:
            return False

        # 2. Increase attempt count (stored in DB)
        OTPRepository.increment_attempts(pending_otp)

        # 3. Check validity
        is_valid = OTPSelectors.is_valid(pending_otp, code)

        if is_valid:
            OTPRepository.mark_used(pending_otp)
            return True

        return False
