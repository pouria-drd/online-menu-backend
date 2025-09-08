import uuid
from django.db import models
from django.utils import timezone
from accounts.utils import normalize_phone
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()


class UserPhoneModel(models.Model):
    """
    Model for storing user phone numbers
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="phones")
    # Phone number is required for user creation and must be unique
    phone_number = models.CharField(
        max_length=11,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^09[0-9]{9}$",
                message="Enter a valid Iranian phone number (e.g., 09123456789).",
                code="invalid_phone",
            )
        ],  # Apply phone number validator
        help_text="Enter a valid Iranian phone number (e.g., 09123456789).",
    )
    # Boolean fields for phone number verification
    is_primary = models.BooleanField(default=False, db_index=True)
    is_verified = models.BooleanField(default=False, db_index=True)
    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "User Phone"
        verbose_name_plural = "User Phones"
        unique_together = ("user", "phone_number")
        ordering = ["-is_primary", "-is_verified", "created_at"]
        indexes = [
            models.Index(fields=["user_id", "is_primary", "is_verified"]),
        ]

    def __str__(self):
        return f"{self.phone_number} ({'primary' if self.is_primary else 'secondary'})"

    def clean(self):
        """Normalize phone number."""
        self.phone_number = normalize_phone(self.phone_number).strip()

    def save(self, *args, **kwargs):
        self.clean()

        if (
            not UserPhoneModel.objects.filter(user=self.user, is_primary=True)
            .exclude(pk=self.pk)
            .exists()
        ):
            # If there is no primary phone number, mark this one as primary
            self.is_primary = True

        elif self.is_primary:
            # If this phone number is primary, only one primary phone number is allowed
            UserPhoneModel.objects.filter(user=self.user, is_primary=True).exclude(
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
