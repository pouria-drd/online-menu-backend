from rest_framework.exceptions import APIException


class EmailServiceError(APIException):
    """Base exception for email service."""

    pass


class TemplateNotFoundError(EmailServiceError):
    """Raised when a template is not found."""

    pass


class EmailSendError(EmailServiceError):
    """Raised when email sending fails."""

    pass
