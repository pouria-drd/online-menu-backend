import hmac
import hashlib
from django.conf import settings
from authentication.constants import OTP_IN_CONSOLE
from authentication.tasks import send_otp_email_task


def hash_code(code: str, salt: str) -> str:
    """
    Securely hash an OTP code using HMAC-SHA256.

    HMAC provides better protection against concatenation and timing attacks
    compared to simple string hashing.
    """
    return hmac.new(salt.encode(), code.encode(), hashlib.sha256).hexdigest()


def log_debug_email(email: str, code: str):
    """Print OTP to console in development mode."""
    print("\n========== OTP Code ==========")
    print(f"Email: {email}")
    print(f"Code:  {code}")
    print("================================\n")


def send_otp_email(email: str, code: str):
    """Send OTP via Celery or log to console depending on settings."""
    if settings.DEBUG and OTP_IN_CONSOLE:
        log_debug_email(email, code)
    else:
        send_otp_email_task.delay(email, code)  # type: ignore
