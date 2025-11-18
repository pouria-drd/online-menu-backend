from django.db import models

from online_menu_backend.env import (
    ENV_MAX_VERIFY_ATTEMPTS,
    ENV_OTP_EXPIRY_MINUTES,
    ENV_OTP_LENGTH,
)

OTP_IN_CONSOLE = True
OTP_LENGTH = ENV_OTP_LENGTH
OTP_EXPIRY_MINUTES = ENV_OTP_EXPIRY_MINUTES
MAX_VERIFY_ATTEMPTS = ENV_MAX_VERIFY_ATTEMPTS


class OTPType(models.TextChoices):
    LOGIN = "login", "Login"
    REGISTER = "register", "Register"
    RESET_PASSWORD = "reset_password", "Reset password"
    VERIFY_EMAIL = "verify_email", "Verify email"
    VERIFY_PHONE = "verify_phone", "Verify phone"


class ChannelType(models.TextChoices):
    EMAIL = "email", "Email"
    PHONE = "phone", "Phone Number"
