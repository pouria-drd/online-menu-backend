import re
from django.core.exceptions import ValidationError


def phone_validator(value):
    """Validate Iranian phone number (e.g., 09123456789)."""
    if not re.match(r"^09[0-9]{9}$", value):
        raise ValidationError("Enter a valid Iranian phone number (e.g., 09123456789).")
