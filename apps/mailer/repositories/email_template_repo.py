from typing import Optional
from django.db.models import QuerySet

from apps.mailer.models import EmailTemplateModel


class EmailTemplateRepository:
    """Repository for EmailTemplate data access."""

    @staticmethod
    def get_by_slug(slug: str, is_active: bool = True) -> Optional[EmailTemplateModel]:
        """Retrieve a template by slug."""
        try:
            return EmailTemplateModel.objects.get(slug=slug, is_active=is_active)
        except EmailTemplateModel.DoesNotExist:
            return None

    @staticmethod
    def get_active_templates() -> QuerySet[EmailTemplateModel]:
        """Get all active templates."""
        return EmailTemplateModel.objects.filter(is_active=True).select_related(
            "created_by"
        )

    @staticmethod
    def create(data: dict) -> EmailTemplateModel:
        """Create a new email template."""
        return EmailTemplateModel.objects.create(**data)

    @staticmethod
    def update(template: EmailTemplateModel, data: dict) -> EmailTemplateModel:
        """Update an existing template."""
        for key, value in data.items():
            setattr(template, key, value)
        template.save()
        return template
