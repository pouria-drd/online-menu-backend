import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import EmailValidator

from ..managers import EmailLogManager
from .email_template_model import EmailTemplateModel
from ..constants import EmailStatus, EmailPriority, DEFAULT_FROM_EMAIL

User = get_user_model()


class EmailLogModel(models.Model):
    """Model for storing email logs, compatible with SQLite and PostgreSQL"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    recipient = models.EmailField(validators=[EmailValidator()])
    sender = models.EmailField(
        default=DEFAULT_FROM_EMAIL, validators=[EmailValidator()]
    )

    cc = models.JSONField(default=list, blank=True)
    bcc = models.JSONField(default=list, blank=True)

    subject = models.CharField(max_length=200)

    body_html = models.TextField()
    body_plain = models.TextField(blank=True)

    template = models.ForeignKey(
        EmailTemplateModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="email_logs",
    )

    status = models.CharField(
        max_length=20,
        choices=EmailStatus.choices,
        default=EmailStatus.PENDING,
        db_index=True,
    )
    priority = models.CharField(
        max_length=20,
        choices=EmailPriority.choices,
        default=EmailPriority.MEDIUM,
    )

    attempts = models.PositiveIntegerField(default=0)

    error_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    objects = EmailLogManager()

    class Meta:
        verbose_name = "Email Log"
        verbose_name_plural = "Email Logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "priority", "created_at"]),
            models.Index(fields=["recipient", "created_at"]),
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self):
        return f"{self.recipient} - {self.subject} ({self.status})"

    # Helper methods to manipulate cc/bcc as lists
    def add_cc(self, email):
        cc_list = self.cc or []
        cc_list.append(email)
        self.cc = cc_list
        self.save()

    def add_bcc(self, email):
        bcc_list = self.bcc or []
        bcc_list.append(email)
        self.bcc = bcc_list
        self.save()
