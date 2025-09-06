import uuid
from django.db import models
from ..constants import EmailType
from ..managers import EmailTemplateManager


class EmailTemplateModel(models.Model):
    """
    A model to store email templates.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100, unique=True, db_index=True, help_text="Name of the template"
    )
    template_type = models.CharField(
        max_length=50, choices=EmailType.choices, db_index=True
    )

    subject = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    body_text = models.TextField(blank=True, help_text="Plain text fallback")
    body_html = models.TextField(
        blank=True, help_text="HTML body with placeholders like {user_name}"
    )

    variables = models.JSONField(
        default=list,
        blank=True,
        help_text="List of variables used in template",
    )

    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = EmailTemplateManager()

    class Meta:
        verbose_name = "Email Template"
        verbose_name_plural = "Email Templates"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["name", "is_active"]),
            models.Index(fields=["template_type", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} - {self.template_type}"

    # Helper methods for variables
    def add_variable(self, var_name: str):
        vars_list = self.variables or []
        if var_name not in vars_list:
            vars_list.append(var_name)
            self.variables = vars_list
            self.save()

    def remove_variable(self, var_name: str):
        vars_list = self.variables or []
        if var_name in vars_list:
            vars_list.remove(var_name)
            self.variables = vars_list
            self.save()
