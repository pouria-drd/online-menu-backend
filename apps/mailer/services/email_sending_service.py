from django.conf import settings
from typing import Dict, Optional, List
from django.template import Context, Template
from django.core.mail import EmailMultiAlternatives

from apps.mailer.models import EmailLogModel
from apps.mailer.exceptions import EmailSendError
from apps.mailer.repositories import EmailLogRepository
from .email_template_service import EmailTemplateService


class EmailSendingService:
    """Service for sending emails."""

    def __init__(self):
        self.template_service = EmailTemplateService()
        self.log_repository = EmailLogRepository()

    def send_email(
        self,
        template_slug: str,
        recipient_email: str,
        context: Dict,
        recipient_name: str = "",
        from_email: Optional[str] = None,
    ) -> EmailLogModel:
        """
        Send an email using a template.

        Args:
            template_slug: The slug of the email template
            recipient_email: Recipient's email address
            context: Dictionary of variables for template rendering
            recipient_name: Optional recipient name
            from_email: Optional sender email (defaults to settings)

        Returns:
            EmailLog: The created log entry
        """
        try:
            # Get and render template
            template = self.template_service.get_template(template_slug)
            html_content, text_content = self.template_service.render_template(
                template, context
            )

            # Render subject with context
            subject = Template(template.subject).render(Context(context))

            # Create log entry
            email_log = self.log_repository.create_log(
                template=template,
                recipient_email=recipient_email,
                subject=subject,
                context_data=context,
                recipient_name=recipient_name,
            )

            # Send email
            self._send_email_message(
                subject=subject,
                text_content=text_content,
                html_content=html_content,
                recipient_email=recipient_email,
                from_email=from_email or settings.DEFAULT_FROM_EMAIL,
                email_log=email_log,
            )

            return email_log

        except Exception as e:
            raise EmailSendError(f"Failed to send email: {str(e)}")

    def _send_email_message(
        self,
        subject: str,
        text_content: str,
        html_content: str,
        recipient_email: str,
        from_email: str,
        email_log: EmailLogModel,
    ):
        """Send the actual email message."""
        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=[recipient_email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)

            self.log_repository.mark_as_sent(email_log)

        except Exception as e:
            self.log_repository.mark_as_failed(email_log, str(e))
            raise

    def send_bulk_emails(
        self, template_slug: str, recipients: List[Dict[str, str]], context: Dict
    ) -> List[EmailLogModel]:
        """
        Send emails to multiple recipients.

        Args:
            template_slug: The slug of the email template
            recipients: List of dicts with 'email' and optional 'name' keys
            context: Base context for all emails

        Returns:
            List of EmailLog entries
        """
        logs = []
        for recipient in recipients:
            try:
                # Create recipient-specific context
                recipient_context = {
                    **context,
                    "recipient_name": recipient.get("name", ""),
                    "recipient_email": recipient["email"],
                }

                log = self.send_email(
                    template_slug=template_slug,
                    recipient_email=recipient["email"],
                    context=recipient_context,
                    recipient_name=recipient.get("name", ""),
                )
                logs.append(log)
            except Exception as e:
                continue

        return logs


# Example usage (method 1)
# from django.http import JsonResponse
# from apps.mailer.services import EmailSendingService


# def my_view(request):
#     service = EmailSendingService()

#     # Send a single email
#     email_log = service.send_email(
#         template_slug="welcome",
#         recipient_email="user@example.com",
#         context={
#             "company_name": "My Company",
#             "user_name": "John Doe",
#             "dashboard_url": "https://example.com/dashboard",
#             "unsubscribe_url": "https://example.com/unsubscribe",
#             "privacy_url": "https://example.com/privacy",
#         },
#         recipient_name="John Doe",
#     )

#     return JsonResponse({"status": "sent", "log_id": email_log.id})


# Example usage (method 2)

# from apps.mailer.tasks import send_email_async, send_bulk_emails_async

# # Send single email asynchronously
# send_email_async.delay(
#     template_slug="welcome",
#     recipient_email="user@example.com",
#     context={"user_name": "John", "company_name": "ACME"},
#     recipient_name="John Doe",
# )  # type: ignore

# # Send bulk emails
# recipients = [
#     {"email": "user1@example.com", "name": "User 1"},
#     {"email": "user2@example.com", "name": "User 2"},
# ]
# send_bulk_emails_async.delay(
#     template_slug="notification",
#     recipients=recipients,
#     context={
#         "notification_type": "Update",
#         "title": "New Features Available",
#         "message": "Check out our latest updates!",
#     },
# )
