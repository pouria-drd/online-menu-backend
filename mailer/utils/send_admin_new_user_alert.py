import logging
from django.conf import settings
from mailer.services import EmailService
from mailer.constants import DEFAULT_FROM_EMAIL

logger = logging.getLogger("mailer")


def send_admin_new_user_alert(user, use_template=True):
    """Send an alert email to admin(s) when a new user is registered."""

    email_service = EmailService()

    role = user.role
    email = user.email
    username = user.username
    registered_at = user.created_at

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
                recipient=admin_email,
                email_type="alert",
                context=context,
                priority="high",
                user=user,
            )
        else:
            email_log = email_service.send_email(
                subject=f"New User Registered",
                recipient=admin_email,
                template_name="admin_new_user_alert",
                context=context,
                priority="high",
                user=user,
            )

    logger.info(f"Admin new user alert email sent to [{admin_emails}]")
