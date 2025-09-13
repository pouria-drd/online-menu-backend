from celery import shared_task
from mailer.services import EmailService
from mailer.constants import EmailPriority
from typing import Dict, List, Optional, Any
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model

User = get_user_model()
logger = get_task_logger("mailer")


@shared_task(name="send_bulk_emails", time_limit=3600, soft_time_limit=3300)
def send_bulk_emails_task(
    name: str,
    recipients: List[str],
    subject: str,
    context: Dict[str, Any],
    use_template: bool = True,
    template_name: Optional[str] = None,
    priority: str = EmailPriority.MEDIUM,
) -> Dict[str, int]:
    """
    Task to send bulk emails asynchronously.

    Args:
        recipients: List of email addresses
        name: Email template name
        subject: Email subject
        context: Email context
        use_template: Whether to use a template or not
        template_name: Template name
        priority: Email priority
        email_type: Email type

    Returns:
        Dict[str, int]: success/failure counts
    """
    failed = 0
    successful = 0
    email_service = EmailService()

    for recipient in recipients:
        user = User.objects.get(email=recipient) if recipient else None
        if not user:
            logger.warning(f"User not found for email {recipient}")
            continue
        try:

            if use_template:
                email_service.send_templated_email(
                    user=user,
                    name=name,
                    context=context,
                    priority=priority,
                    recipient=recipient,
                )
            else:

                email_service.send_email(
                    user=user,
                    subject=subject,
                    context=context,
                    priority=priority,
                    recipient=recipient,
                    template_name=template_name,
                )

            logger.info(f"Email successfully sent to {recipient}")
            successful += 1

        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {str(e)}")
            failed += 1

    logger.info(f"Bulk email completed: {successful} sent, {failed} failed")
    return {
        "successful": successful,
        "failed": failed,
        "total": len(recipients),
    }
