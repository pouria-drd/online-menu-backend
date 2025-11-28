from celery import shared_task

from config.env import ENV_MAX_RETRY_ATTEMPTS
from apps.mailer.services import EmailSendingService


@shared_task(bind=True, max_retries=ENV_MAX_RETRY_ATTEMPTS)
def send_email_async(self, template_slug, recipient_email, context, recipient_name=""):
    """
    Celery task to send emails asynchronously.

    Args:
        template_slug: The slug of the email template
        recipient_email: Recipient's email address
        context: Dictionary of variables for template rendering
        recipient_name: Optional recipient name
    """
    try:
        service = EmailSendingService()
        email_log = service.send_email(
            template_slug=template_slug,
            recipient_email=recipient_email,
            context=context,
            recipient_name=recipient_name,
        )
        return {
            "status": "success",
            "log_id": email_log.id,
            "recipient": recipient_email,
        }
    except Exception as e:
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2**self.request.retries))


@shared_task
def send_bulk_emails_async(template_slug, recipients, context):
    """
    Celery task to send bulk emails asynchronously.

    Args:
        template_slug: The slug of the email template
        recipients: List of dicts with 'email' and optional 'name' keys
        context: Base context for all emails
    """
    service = EmailSendingService()
    results = service.send_bulk_emails(
        template_slug=template_slug, recipients=recipients, context=context
    )
    return {
        "total": len(recipients),
        "sent": len([r for r in results if r.status == "SENT"]),
        "failed": len([r for r in results if r.status == "FAILED"]),
    }
