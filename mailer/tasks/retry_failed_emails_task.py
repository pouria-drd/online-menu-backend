from celery import shared_task
from celery.utils.log import get_task_logger
from mailer.services.email_service import EmailService

logger = get_task_logger("mailer")


@shared_task(name="retry_failed_emails", time_limit=1800)  # 30 minutes
def retry_failed_emails_task(limit: int = 100) -> int:
    """
    Task to retry failed emails.

    Args:
        limit (int): The maximum number of emails to retry.

    Returns:
        int: The number of emails retried.
    """

    email_service = EmailService()
    retry_count = email_service.retry_failed_emails(limit=limit)

    logger.info(f"Retried {retry_count} failed emails")
    return retry_count
