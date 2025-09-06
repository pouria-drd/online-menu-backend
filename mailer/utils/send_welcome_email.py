from django.utils import timezone
from mailer.services.email_service import EmailService


def send_welcome_email(user):
    """Send welcome email to user"""

    email_service = EmailService()

    user_name = user.username
    activation_link = "https://pouria-drd.ir"
    current_year = timezone.now().year

    context = {
        "user_name": user_name,
        "site_name": "Online Menu",
        "current_year": current_year,
        "activation_link": activation_link,
    }

    email_log = email_service.send_email(
        recipient=user.email,
        subject=f"Welcome {user_name}!",
        template_name="welcome",
        context=context,
        priority="high",
        user=user,
    )

    print(email_log.status)
    print(email_log.attempts)
