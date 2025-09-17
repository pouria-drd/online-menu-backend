import logging
from django.utils import timezone
from mailer.constants import EmailPriority
from mailer.tasks import send_single_email_task

logger = logging.getLogger("mailer")


def send_welcome_email(user) -> str | None:
    """Send welcome email to user asynchronously via Celery"""

    user_name = getattr(user, "username", "User")
    user_email = getattr(user, "email", None)

    if not user_email:
        return None

    activation_link = "https://pouria-drd.ir"
    current_year = timezone.now().year

    context = {
        "user_name": user_name,
        "site_name": "Online Menu",
        "current_year": current_year,
        "activation_link": activation_link,
    }

    try:
        task = send_single_email_task.delay(
            context=context,
            use_template=False,
            name="Welcome Email",
            recipient=user_email,
            template_name="welcome",
            priority=EmailPriority.HIGH,
            subject=f"Welcome {user_name}!",
        )  # type: ignore
        return getattr(task, "id", None)
    except AttributeError as e:
        return None
