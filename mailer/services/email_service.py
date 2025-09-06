import logging
from django.utils import timezone
from typing import List, Dict, Optional, Any
from django.core.mail import EmailMultiAlternatives

from .template_service import TemplateService
from ..models import (
    EmailLogModel,
    EmailTemplateModel,
    EmailBlacklistModel,
    EmailAttachmentModel,
)
from ..constants import EmailStatus, EmailPriority, DEFAULT_FROM_EMAIL

logger = logging.getLogger("mailer")


class EmailService:
    """Main service for managing emails"""

    def __init__(self):
        self.template_service = TemplateService()

    def send_email(
        self,
        recipient: str,
        subject: str,
        template_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        html_content: Optional[str] = None,
        plain_content: Optional[str] = None,
        sender: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Dict]] = None,
        priority: str = EmailPriority.MEDIUM,
        user=None,
        metadata: Optional[Dict] = None,
    ) -> EmailLogModel:
        """
        Send an email with complete features
        """
        # Blacklist check
        if self._is_blacklisted(recipient):
            logger.warning(f"Email to {recipient} blocked - blacklisted")
            return self._create_log(
                recipient=recipient,
                subject=subject,
                status=EmailStatus.FAILED,
                error_message="Recipient is blacklisted",
            )

        # Render template
        if template_name:
            html_content, plain_content = self.template_service.render_template(
                template_name, context or {}
            )

        if not html_content and not plain_content:
            raise ValueError("Email must have either HTML or plain text content")

        # Creating log
        email_log: EmailLogModel = self._create_log(
            recipient=recipient,
            subject=subject,
            body_html=html_content or "",
            body_plain=plain_content or "",
            sender=sender or DEFAULT_FROM_EMAIL,
            cc=cc,
            bcc=bcc,
            priority=priority,
            user=user,
            metadata=metadata or {},
        )

        try:
            # Create email
            email = self._create_email_message(
                recipient=recipient,
                subject=subject,
                html_content=html_content,
                plain_content=plain_content,
                sender=sender or DEFAULT_FROM_EMAIL,
                cc=cc,
                bcc=bcc,
            )

            # Add attachments
            if attachments:
                self._add_attachments(email, attachments, email_log)

            # Send email
            email.send(fail_silently=False)

            # Update log
            email_log.status = EmailStatus.SENT
            email_log.sent_at = timezone.now()
            email_log.attempts += 1
            email_log.save()

            logger.info(f"Email sent successfully to {recipient}")
            return email_log

        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {str(e)}")
            email_log.status = EmailStatus.FAILED
            email_log.error_message = str(e)
            email_log.attempts += 1
            email_log.save()
            raise

    def send_bulk_emails(
        self,
        recipients: List[str],
        subject: str,
        template_name: str,
        base_context: Optional[Dict] = None,
        personalized_contexts: Optional[Dict[str, Dict]] = None,
        priority: str = EmailPriority.LOW,
    ) -> List[EmailLogModel]:
        """
        Send a bulk email with personalized contexts
        """
        email_logs: List[EmailLogModel] = []
        base_context = base_context or {}

        for recipient in recipients:
            try:
                # Override context with personalized context
                context = base_context.copy()
                if personalized_contexts and recipient in personalized_contexts:
                    context.update(personalized_contexts[recipient])

                email_log: EmailLogModel = self.send_email(
                    recipient=recipient,
                    subject=subject,
                    template_name=template_name,
                    context=context,
                    priority=priority,
                )
                email_logs.append(email_log)

            except Exception as e:
                logger.error(f"Failed to send bulk email to {recipient}: {str(e)}")
                continue

        return email_logs

    def send_templated_email(
        self, recipient: str, email_type: str, context: Dict[str, Any], **kwargs
    ) -> EmailLogModel:
        """
        Send an email with a template from the database
        """
        template: EmailTemplateModel = EmailTemplateModel.objects.get_by_type(email_type)  # type: ignore
        if not template:
            raise ValueError(f"No active template found for type: {email_type}")

        # Render template with context
        rendered_subject = self.template_service.render_string(
            template.subject, context
        )
        rendered_html = self.template_service.render_string(template.body_html, context)
        rendered_plain = (
            self.template_service.render_string(template.body_text, context)
            if template.body_text
            else None
        )

        return self.send_email(
            recipient=recipient,
            subject=rendered_subject,
            html_content=rendered_html,
            plain_content=rendered_plain,
            **kwargs,
        )

    def retry_failed_emails(self, limit: int = 50) -> int:
        """
        Retry failed emails
        """
        failed_emails: List[EmailLogModel] = EmailLogModel.objects.retry_failed()[  # type: ignore
            :limit
        ]
        retry_count = 0

        for email_log in failed_emails:
            try:
                email = self._create_email_message(
                    recipient=email_log.recipient,
                    subject=email_log.subject,
                    html_content=email_log.body_html,
                    plain_content=email_log.body_plain,
                    sender=email_log.sender,
                    cc=email_log.cc,
                    bcc=email_log.bcc,
                )

                email.send(fail_silently=False)

                email_log.status = EmailStatus.SENT
                email_log.sent_at = timezone.now()
                email_log.attempts += 1
                email_log.save()

                retry_count += 1
                logger.info(f"Successfully retried email to {email_log.recipient}")

            except Exception as e:
                email_log.attempts += 1
                email_log.error_message = str(e)
                email_log.save()
                logger.error(f"Retry failed for {email_log.recipient}: {str(e)}")

        return retry_count

    def _is_blacklisted(self, email: str) -> bool:
        """Check if email is blacklisted"""
        return EmailBlacklistModel.objects.filter(email=email, is_active=True).exists()

    def _create_log(self, **kwargs) -> EmailLogModel:
        """Create log"""
        return EmailLogModel.objects.create(**kwargs)

    def _create_email_message(
        self,
        recipient: str,
        subject: str,
        html_content: Optional[str] = None,
        plain_content: Optional[str] = None,
        sender: str = DEFAULT_FROM_EMAIL,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> EmailMultiAlternatives:
        """Create email object"""
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_content or "",
            from_email=sender,
            to=[recipient],
            cc=cc or [],
            bcc=bcc or [],
        )

        if html_content:
            email.attach_alternative(html_content, "text/html")

        return email

    def _add_attachments(
        self,
        email: EmailMultiAlternatives,
        attachments: List[Dict],
        email_log: EmailLogModel,
    ):
        """Add attachments to email"""
        for attachment in attachments:
            email.attach(
                attachment["filename"],
                attachment["content"],
                attachment.get("content_type", "application/octet-stream"),
            )

            # Save attachment info to database
            EmailAttachmentModel.objects.create(
                email_log=email_log,
                filename=attachment["filename"],
                content_type=attachment.get("content_type", "application/octet-stream"),
                size=len(attachment["content"]),
            )
