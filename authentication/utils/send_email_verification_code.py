from django.utils import timezone
from mailer.constants import EmailPriority
from mailer.tasks import send_single_email_task
from authentication.constants import OTP_EXPIRY_MINUTES

expiry_minutes = OTP_EXPIRY_MINUTES


def send_email_verification_code(user, verification_code) -> str | None:
    """Send email verification code to user asynchronously via Celery"""

    username = getattr(user, "username", "User")
    user_email = getattr(user, "email", None)

    if not user_email:
        return None

    current_year = timezone.now().year

    context = {
        "username": username,
        "verification_code": verification_code,
        "current_year": current_year,
        "expiry_minutes": expiry_minutes,
    }

    try:
        task = send_single_email_task.delay(
            context=context,
            use_template=False,
            recipient=user_email,
            name="Email Verification",
            priority=EmailPriority.HIGH,
            template_name="email_verification",
            subject="Verify Your Email Address",
        )  # type: ignore
        return getattr(task, "id", None)
    except AttributeError as e:
        return None
