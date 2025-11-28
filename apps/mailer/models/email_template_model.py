import uuid
from django.db import models
from apps.mailer.constants import TemplateType


class EmailTemplateModel(models.Model):
    """
    A model to store email templates.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(
        max_length=255, unique=True, help_text="Unique template name"
    )
    slug = models.SlugField(
        max_length=255, unique=True, help_text="URL-friendly template identifier"
    )

    subject = models.CharField(max_length=255, help_text="Email subject line")
    description = models.TextField(blank=True)

    html_content = models.TextField(
        help_text="HTML content of the email. Use {{ variable }} for placeholders"
    )

    text_content = models.TextField(
        blank=True, help_text="Plain text version (optional, auto-generated if empty)"
    )

    template_type = models.CharField(
        max_length=20, choices=TemplateType.choices, default=TemplateType.CUSTOM
    )

    variables = models.JSONField(
        default=list,
        blank=True,
        help_text="List of variables used in template",
    )

    is_active = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Email Template"
        verbose_name_plural = "Email Templates"
        indexes = [
            models.Index(fields=["slug", "is_active"]),
            models.Index(fields=["template_type", "is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.template_type})"
