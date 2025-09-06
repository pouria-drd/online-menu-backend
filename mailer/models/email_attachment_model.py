import os
import uuid
import mimetypes
from django.db import models
from datetime import datetime
from .email_log_model import EmailLogModel
from django.utils.text import get_valid_filename


def normalize_filename(filename: str) -> str:
    """
    Normalize a filename:
    - lowercase
    - spaces → underscores
    - safe characters
    - uuid prefix
    """
    base, ext = os.path.splitext(filename)
    normalized = get_valid_filename(base).lower().replace(" ", "_")
    return f"{uuid.uuid4().hex}_{normalized}{ext.lower()}"


def upload_to(instance, filename):
    """
    Generate dynamic upload path:
    mailer/email_attachments/YYYY/MM/DD/<normalized_filename>
    """
    today = datetime.now()
    normalized = normalize_filename(filename)

    # Keep normalized name for DB field
    instance.filename = normalized

    return os.path.join(
        "mailer",
        "email_attachments",
        str(today.year),
        str(today.month).zfill(2),
        str(today.day).zfill(2),
        normalized,
    )


class EmailAttachmentModel(models.Model):
    """
    Model for storing email attachments
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email_log = models.ForeignKey(
        EmailLogModel, on_delete=models.CASCADE, related_name="attachments"
    )
    file = models.FileField(upload_to=upload_to)
    filename = models.CharField(max_length=255, blank=True, null=True)
    content_type = models.CharField(max_length=100, blank=True, null=True)
    size = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Email Attachment"
        verbose_name_plural = "Email Attachments"

    def __str__(self):
        return f"{self.filename or 'unnamed'} - {self.email_log.recipient}"

    def save(self, *args, **kwargs):
        if self.file:
            # Ensure filename is always normalized (if missing, upload_to handles it)
            if not self.filename:
                self.filename = os.path.basename(self.file.name)

            if not self.content_type:
                mime_type, _ = mimetypes.guess_type(self.file.name)
                self.content_type = mime_type or "application/octet-stream"

            if not self.size:
                try:
                    self.size = self.file.size
                except Exception:
                    self.size = 0

        super().save(*args, **kwargs)
