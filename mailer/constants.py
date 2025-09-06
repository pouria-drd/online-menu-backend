import os
from django.db import models
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend"
)

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@example.com")
MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", 3))


class EmailStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SENT = "sent", "Sent"
    FAILED = "failed", "Failed"
    BOUNCED = "bounced", "Bounced"
    DELIVERED = "delivered", "Delivered"
    OPENED = "opened", "Opened"
    CLICKED = "clicked", "Clicked"


class EmailPriority(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    CRITICAL = "critical", "Critical"


class EmailType(models.TextChoices):
    ALERT = "alert", "Alert"
    REPORT = "report", "Report"
    WELCOME = "welcome", "Welcome"
    INVOICE = "invoice", "Invoice"
    REMINDER = "reminder", "Reminder"
    MARKETING = "marketing", "Marketing"
    PASSWORD_RESET = "password_reset", "Password Reset"
    VERIFICATION = "verification", "Email Verification"
    ORDER_STATUS = "order_status", "Order Status Update"
    NOTIFICATION = "notification", "General Notification"
    ORDER_CONFIRMATION = "order_confirmation", "Order Confirmation"
