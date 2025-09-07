import re
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


def email_validator(value):
    """Validate email format."""
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", value):
        raise ValidationError("Enter a valid email address.")

    # Check if the email is valid
    try:
        validate_email(value)
    except ValidationError:
        raise ValidationError("Enter a valid email address.")
