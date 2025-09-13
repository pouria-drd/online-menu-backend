import logging
from django.utils import timezone
from mailer.constants import EmailPriority
from mailer.tasks import send_single_email_task

logger = logging.getLogger("mailer")


def send_welcome_email_task(user, use_template=True, **kwargs) -> str | None:
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
            name="Welcome Email",
            recipient=user_email,
            template_name="welcome",
            use_template=use_template,
            priority=EmailPriority.HIGH,
            subject=f"Welcome {user_name}!",
            **kwargs,
        )  # type: ignore
        return getattr(task, "id", None)
    except AttributeError as e:
        return None


def send_welcome_email(user, use_template=True):
    """Send welcome email to user"""
    from mailer.services import EmailService

    email_service = EmailService()

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

    if use_template:
        email_log = email_service.send_templated_email(
            user=user,
            context=context,
            recipient=user_email,
            name="Welcome Email",
            priority=EmailPriority.HIGH,
        )
    else:
        email_log = email_service.send_email(
            user=user,
            context=context,
            recipient=user_email,
            template_name="welcome",
            priority=EmailPriority.HIGH,
            subject=f"Welcome {user_name}!",
        )

    logger.info(
        f"Welcome email sent to {user_name} ({user_email}) - Log ID: {email_log.id}"
    )
