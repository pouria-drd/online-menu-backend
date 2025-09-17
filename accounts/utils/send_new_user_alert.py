from datetime import datetime
from django.contrib.auth import get_user_model

from mailer.constants import EmailPriority
from mailer.tasks import send_bulk_emails_task


User = get_user_model()


def send_new_user_alert(user):
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
        "current_year": datetime.now().year,
    }

    try:
        admins = User.objects.filter(role="admin")
        admin_emails = [admin.email for admin in admins]

        task = send_bulk_emails_task.delay(
            context=context,
            use_template=False,
            recipients=admin_emails,
            name="New User Registered",
            priority=EmailPriority.HIGH,
            subject="New User Registered",
            template_name="new_user_alert",
        )  # type: ignore
        return getattr(task, "id", None)
    except AttributeError as e:
        return None
