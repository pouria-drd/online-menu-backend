from django.template.loader import get_template
from django.core.management.base import BaseCommand

from apps.mailer.constants import TemplateType
from apps.mailer.models import EmailTemplateModel
from apps.mailer.validators import TemplateValidator


class Command(BaseCommand):
    """Management command to load predefined email templates."""

    help = "Load predefined email templates from templates directory"

    TEMPLATES = [
        {
            "name": "OTP Verification",
            "slug": "otp-verification",
            "subject": "Your Verification Code - {{ site_name }}",
            "template_file": "email_templates/otp.html",
            "variables": [
                "name",
                "otp_code",
                "expiry_minutes",
                "site_name",
                "support_email",
            ],
        }
    ]

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write("Loading email templates...")

        for template_data in self.TEMPLATES:
            try:
                # Load template content from file
                template = get_template(template_data["template_file"])
                html_content = template.template.source  # type: ignore

                # Validate template syntax
                TemplateValidator.validate_template_syntax(html_content)

                # Create or update template
                obj, created = EmailTemplateModel.objects.update_or_create(
                    slug=template_data["slug"],
                    defaults={
                        "name": template_data["name"],
                        "subject": template_data["subject"],
                        "html_content": html_content,
                        "template_type": TemplateType.CUSTOM,
                        "variables": template_data["variables"],
                        "is_active": True,
                    },
                )

                action = "Created" if created else "Updated"
                self.stdout.write(
                    self.style.SUCCESS(f'{action}: {template_data["name"]}')
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error loading {template_data["name"]}: {str(e)}')
                )

        self.stdout.write(self.style.SUCCESS("\nTemplate loading complete!"))
