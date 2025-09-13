import logging
from django.conf import settings
from mailer.services import EmailService
from mailer.tasks import send_bulk_emails_task
from mailer.constants import DEFAULT_FROM_EMAIL, EmailPriority

logger = logging.getLogger("mailer")


def send_admin_new_user_alert_task(user, use_template=True):
    """Send an alert email to admin(s) asynchronously via Celery."""

    role = getattr(user, "role", "User")
    email = getattr(user, "email", None)
    username = getattr(user, "username", "User")
    registered_at = getattr(user, "created_at", None)

    if not email:
        return None

    context = {
        "role": role,
        "email": email,
        "username": username,
        "registered_at": registered_at,
    }

    admin_emails = getattr(settings, "ADMIN_EMAILS", [DEFAULT_FROM_EMAIL])

    try:
        task = send_bulk_emails_task.delay(
            context=context,
            recipients=admin_emails,
            use_template=use_template,
            name="New User Registered",
            priority=EmailPriority.HIGH,
            subject="New User Registered",
            template_name="admin_new_user_alert",
        )  # type: ignore
        return getattr(task, "id", None)
    except AttributeError as e:
        return None


def send_admin_new_user_alert(user, use_template=True):
    """Send an alert email to admin(s) when a new user is registered."""

    email_service = EmailService()

    role = getattr(user, "role", "User")
    email = getattr(user, "email", None)
    username = getattr(user, "username", "User")
    registered_at = getattr(user, "created_at", None)

    if not email:
        return None

    context = {
        "role": role,
        "email": email,
        "username": username,
        "registered_at": registered_at,
    }

    admin_emails = getattr(settings, "ADMIN_EMAILS", [DEFAULT_FROM_EMAIL])

    for admin_email in admin_emails:
        if use_template:
            email_log = email_service.send_templated_email(
                user=user,
                context=context,
                recipient=admin_email,
                name="New User Registered",
                priority=EmailPriority.HIGH,
            )
        else:
            email_log = email_service.send_email(
                user=user,
                context=context,
                recipient=admin_email,
                priority=EmailPriority.HIGH,
                subject=f"New User Registered",
                template_name="admin_new_user_alert",
            )

    logger.info(f"Admin new user alert email sent to [{admin_emails}]")
