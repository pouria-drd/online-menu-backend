from django.utils import timezone
from django.db.models import QuerySet

from apps.mailer.constants import EmailStatus
from apps.mailer.models import EmailTemplateModel, EmailLogModel


class EmailLogRepository:
    """Repository for EmailLog data access."""

    @staticmethod
    def create_log(
        template: EmailTemplateModel,
        recipient_email: str,
        subject: str,
        context_data: dict,
        recipient_name: str = "",
    ) -> EmailLogModel:
        """Create a new email log entry."""
        return EmailLogModel.objects.create(
            template=template,
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            subject=subject,
            context_data=context_data,
        )

    @staticmethod
    def get_by_recipient(email: str) -> QuerySet[EmailLogModel]:
        """Get all logs for a specific recipient."""
        return EmailLogModel.objects.filter(recipient_email=email).select_related(
            "template"
        )

    @staticmethod
    def get_failed_logs() -> QuerySet[EmailLogModel]:
        """Get all failed email logs."""
        return EmailLogModel.objects.filter(status=EmailStatus.FAILED)

    @staticmethod
    def mark_as_sent(log: EmailLogModel) -> EmailLogModel:
        """Mark email as successfully sent."""
        log.status = EmailStatus.SENT
        log.sent_at = timezone.now()
        log.save(update_fields=["status", "sent_at", "updated_at"])
        log.refresh_from_db()
        return log

    @staticmethod
    def mark_as_failed(log: EmailLogModel, error_message: str) -> EmailLogModel:
        """Mark email as failed with error message."""
        log.status = EmailStatus.FAILED
        log.error_message = error_message
        log.save(update_fields=["status", "error_message", "updated_at"])
        log.refresh_from_db()
        return log
