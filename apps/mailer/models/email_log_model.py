import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import EmailValidator

from apps.mailer.constants import EmailStatus
from .email_template_model import EmailTemplateModel

User = get_user_model()


class EmailLogModel(models.Model):
    """
    A model to log email sending activities.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    template = models.ForeignKey(
        EmailTemplateModel, on_delete=models.SET_NULL, null=True, related_name="logs"
    )

    subject = models.CharField(max_length=255)

    recipient_name = models.CharField(max_length=255, blank=True)
    recipient_email = models.EmailField(validators=[EmailValidator()], db_index=True)

    status = models.CharField(
        max_length=20,
        choices=EmailStatus.choices,
        default=EmailStatus.PENDING,
        db_index=True,
    )

    context_data = models.JSONField(
        default=dict, blank=True, help_text="Variables used in the email"
    )

    error_message = models.TextField(blank=True)

    sent_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Email Log"
        verbose_name_plural = "Email Logs"
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["recipient_email", "created_at"]),
        ]

    def __str__(self):
        return f"{self.recipient_email} - {self.subject} ({self.status})"
