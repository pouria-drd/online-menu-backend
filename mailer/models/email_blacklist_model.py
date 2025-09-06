import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import EmailValidator

User = get_user_model()


class EmailBlacklistModel(models.Model):
    """
    Model for storing email blacklists
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="blacklisted_emails",
    )

    reason = models.TextField()
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_blacklists"
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Email Blacklist"
        verbose_name_plural = "Email Blacklists"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} - {'Active' if self.is_active else 'Inactive'}"
