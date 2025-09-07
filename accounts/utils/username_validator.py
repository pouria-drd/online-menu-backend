import re
from django.core.exceptions import ValidationError


def username_validator(value):
    """Validate username: letters, digits, and underscore only."""
    if not re.match(r"^[a-zA-Z0-9_]+$", value):
        raise ValidationError(
            "Username can only contain letters, digits, and underscores."
        )
    if len(value) < 3:
        raise ValidationError("Username must be at least 3 characters long.")
