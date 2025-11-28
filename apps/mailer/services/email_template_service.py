from typing import Dict
from html import unescape
from django.template import Context, Template

from apps.mailer.models import EmailTemplateModel
from apps.mailer.exceptions import TemplateNotFoundError
from apps.mailer.repositories import EmailTemplateRepository


class EmailTemplateService:
    """Service for email template operations."""

    def __init__(self):
        self.repository = EmailTemplateRepository()

    def get_template(self, slug: str) -> EmailTemplateModel:
        """Retrieve a template by slug."""
        template = self.repository.get_by_slug(slug)
        if not template:
            raise TemplateNotFoundError(f"Template with slug '{slug}' not found")
        return template

    def render_template(
        self, template: EmailTemplateModel, context: Dict
    ) -> tuple[str, str]:
        """
        Render both HTML and text content with context variables.

        Returns:
            tuple: (rendered_html, rendered_text)
        """
        html_template = Template(template.html_content)
        html_content = html_template.render(Context(context))

        if template.text_content:
            text_template = Template(template.text_content)
            text_content = text_template.render(Context(context))
        else:
            # Auto-generate plain text from HTML
            text_content = self._html_to_text(html_content)

        return html_content, text_content

    @staticmethod
    def _html_to_text(html: str) -> str:
        """Convert HTML to plain text (basic implementation)."""
        from django.utils.html import strip_tags

        return unescape(strip_tags(html))
