import logging
from celery import shared_task

logger = logging.getLogger(__name__)


# TODO: Add custom template id
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_otp_email_task(self, email: str, code: str):
    """
    Send SMS asynchronously via Celery.
    Retries on failure up to 3 times.
    """
    try:
        print(f"Sending SMS to {email} with code {code}")
        # success = send_otp_email(email, code)
        # if not success:
        # raise Exception("SMS sending failed")
    except Exception as exc:
        logger.error(f"Retrying SMS to {email} due to error: {exc}")
        raise self.retry(exc=exc)
