import os
from django.db import models
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", 5))  # in minutes


class UseCase(models.TextChoices):
    EMAIL_2FA = "email_2fa", "Email 2FA"
    EMAIL_VERIFICATION = "email_verification", "Email Verification"
