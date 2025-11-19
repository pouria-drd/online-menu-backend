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
    VERIFY_EMAIL = "verify_email", "Verify email"
    RESET_PASSWORD = "reset_password", "Reset password"
