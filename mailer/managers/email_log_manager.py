from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q, Count, Avg


class EmailLogManager(models.Manager):
    """Manager for EmailLog model"""

    def pending(self):
        """Emails in pending status"""
        from ..constants import EmailStatus

        return self.filter(status=EmailStatus.PENDING)

    def failed(self):
        """Emails in failed status"""
        from ..constants import EmailStatus

        return self.filter(status=EmailStatus.FAILED)

    def sent_today(self):
        """Emails sent today"""
        from ..constants import EmailStatus

        today = timezone.now().date()
        return self.filter(status=EmailStatus.SENT, sent_at__date=today)

    def by_priority(self):
        """Sort by priority"""
        from ..constants import EmailPriority

        priority_order = models.Case(
            models.When(priority=EmailPriority.CRITICAL, then=1),
            models.When(priority=EmailPriority.HIGH, then=2),
            models.When(priority=EmailPriority.MEDIUM, then=3),
            models.When(priority=EmailPriority.LOW, then=4),
            default=5,
            output_field=models.IntegerField(),
        )
        return self.annotate(priority_order=priority_order).order_by(
            "priority_order", "created_at"
        )

    def retry_failed(self):
        """Emails that can be retried"""
        from ..constants import EmailStatus, MAX_RETRY_ATTEMPTS

        one_hour_ago = timezone.now() - timedelta(hours=1)
        return self.filter(
            status=EmailStatus.FAILED,
            attempts__lt=MAX_RETRY_ATTEMPTS,
            updated_at__lt=one_hour_ago,
        )

    def get_statistics(self, days=7):
        """Email statistics for the last N days"""
        from ..constants import EmailStatus

        start_date = timezone.now() - timedelta(days=days)

        return self.filter(created_at__gte=start_date).aggregate(
            total=Count("id"),
            sent=Count("id", filter=Q(status=EmailStatus.SENT)),
            failed=Count("id", filter=Q(status=EmailStatus.FAILED)),
            pending=Count("id", filter=Q(status=EmailStatus.PENDING)),
            avg_attempts=Avg("attempts"),
        )
