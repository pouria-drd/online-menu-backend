from celery import shared_task
from typing import Dict, Any, Optional
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model

from mailer.constants import EmailPriority
from mailer.services.email_service import EmailService

User = get_user_model()
logger = get_task_logger("mailer")


@shared_task(
    bind=True,
    name="send_single_email",
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
    autoretry_for=(Exception,),
)
def send_single_email_task(
    self,
    name: str,
    subject: str,
    recipient: str,
    context: Dict[str, Any],
    use_template: bool = True,
    template_name: Optional[str] = None,
    priority: str = EmailPriority.MEDIUM,
    **kwargs,
) -> bool:
    """
    Task to send a single email.

    Args:
        name (str): The name of the template to use for the email.
        recipient (str): The email address of the recipient.
        subject (str): The subject of the email.
        template_name (Optional[str]): The name of the template to use for the email.
        context (Optional[Dict[str, Any]]): The context to use for the email template.
        priority (str): The priority of the email.
        use_template (bool): Whether to use the template or not.
        **kwargs: Additional keyword arguments to pass to the email service.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    try:
        email_service = EmailService()
        user = User.objects.get(email=recipient) if recipient else None

        if not user:
            logger.warning(f"User not found for email {recipient}")
            return False

        if use_template:
            email_log = email_service.send_templated_email(
                user=user,
                name=name,
                context=context,
                priority=priority,
                recipient=recipient,
                **kwargs,
            )

        else:
            email_log = email_service.send_email(
                user=user,
                subject=subject,
                context=context,
                priority=priority,
                recipient=recipient,
                template_name=template_name,
                **kwargs,
            )

        logger.info(f"Email sent successfully to {recipient} - Log ID: {email_log.id}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {str(e)}")
        raise self.retry(exc=e)
