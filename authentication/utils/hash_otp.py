import hmac
import hashlib
from django.conf import settings

OTP_SECRET_KEY = settings.SECRET_KEY


def hash_otp(otp: str) -> str:
    """Hash OTP with HMAC using SECRET_KEY"""
    return hmac.new(OTP_SECRET_KEY.encode(), otp.encode(), hashlib.sha256).hexdigest()
