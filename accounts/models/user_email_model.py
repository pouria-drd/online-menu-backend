import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import EmailValidator

User = get_user_model()


class UserEmailModel(models.Model):
    """
    Model for storing user emails
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="emails")
    # Email is required for user creation and must be unique
    email = models.EmailField(
        unique=True,
        db_index=True,
        validators=[
            EmailValidator(
                message="Enter a valid email address.",
                code="invalid_email",
            )
        ],
        help_text="Enter a valid email address.",
    )
    # Boolean fields for email verification
    is_primary = models.BooleanField(
        default=False,
        db_index=True,
    )
    is_verified = models.BooleanField(
        default=False,
        db_index=True,
    )
    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "User Email"
        verbose_name_plural = "User Emails"
        unique_together = ("user", "email")
        ordering = ["-is_primary", "-is_verified", "created_at"]
        indexes = [
            models.Index(fields=["user_id", "is_primary", "is_verified"]),
        ]

    def __str__(self):
        return f"{self.email} ({'primary' if self.is_primary else 'secondary'})"

    def clean(self):
        """Normalize email."""
        self.email = self.email.lower().strip()

    def save(self, *args, **kwargs):
        self.clean()

        if (
            not UserEmailModel.objects.filter(user=self.user, is_primary=True)
            .exclude(pk=self.pk)
            .exists()
        ):
            # If there is no primary email, mark this one as primary
            self.is_primary = True

        elif self.is_primary:
            # If this email is primary, only one primary email is allowed
            UserEmailModel.objects.filter(user=self.user, is_primary=True).exclude(
                pk=self.pk
            ).update(is_primary=False)

        super().save(*args, **kwargs)

    def mark_as_verified(self):
        self.is_verified = True
        self.verified_at = timezone.now()
        self.save()

    def mark_as_unverified(self):
        self.is_verified = False
        self.verified_at = None
        self.save()
