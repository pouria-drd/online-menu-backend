import uuid
from accounts.managers import UserManager
from accounts.constants import UserRole, UserStatus

from django.db import models
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import EmailValidator, RegexValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


class UserModel(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that replaces Django's default user model.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Username is required and must be unique
    username = models.CharField(
        unique=True,
        max_length=25,
        validators=[
            RegexValidator(
                regex=r"^[a-z0-9_]{1,25}$",
                message="Username can only contain lowercase letters, numbers, and underscores and must be at most 25 characters long.",
                code="invalid_username",
            )
        ],  # Apply username validator
        help_text="Required. 25 characters or fewer. Letters, digits, and _ only.",
    )
    # Status for the user (active, banned, deleted)
    status = models.CharField(
        max_length=20,
        choices=UserStatus.choices,
        default=UserStatus.ACTIVE,
        db_index=True,
    )
    # Role for the user (admin, user, menu owner)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.USER,
        db_index=True,
    )
    # Timestamps for user creation and last update
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Attach the custom manager
    objects = UserManager()

    # Set the USERNAME_FIELD to 'username' for login
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    class Meta:
        """Meta class for the UserModel."""

        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        """String representation of the user."""
        username = self.username
        return username

    # OPTIMIZED: Use cached properties to avoid repeated queries
    @property
    def primary_email(self):
        """Get primary email from prefetched data if available, otherwise query"""
        # If emails are prefetched with primary filter, use first()
        if hasattr(self, "_prefetched_objects_cache") and "emails" in self._prefetched_objects_cache:  # type: ignore
            emails = [e for e in self.emails.all() if e.is_primary]  # type: ignore
            return emails[0].email if emails else None

        # Fallback to database query with select_related optimization
        email_obj = self.emails.filter(is_primary=True).first()  # type: ignore
        return email_obj.email if email_obj else None

    @property
    def primary_phone(self):
        """Get primary phone from prefetched data if available, otherwise query"""
        # If phones are prefetched with primary filter, use first()
        if hasattr(self, "_prefetched_objects_cache") and "phones" in self._prefetched_objects_cache:  # type: ignore
            phones = [p for p in self.phones.all() if p.is_primary]  # type: ignore
            return phones[0].phone_number if phones else None

        # Fallback to database query with select_related optimization
        phone_obj = self.phones.filter(is_primary=True).first()  # type: ignore
        return phone_obj.phone_number if phone_obj else None

    @property
    def is_staff(self) -> bool:
        """Check if the user is staff."""
        status: bool = self.role == UserRole.ADMIN
        return status

    @property
    def is_active(self) -> bool:
        """Check if the user is active."""
        status: bool = self.status == UserStatus.ACTIVE
        return status

    @property
    def email_verified(self) -> bool:
        """Check if the user's email is verified - optimized version"""
        if hasattr(self, "_prefetched_objects_cache") and "emails" in self._prefetched_objects_cache:  # type: ignore
            emails = [e for e in self.emails.all() if e.is_primary]  # type: ignore
            return emails[0].is_verified if emails else False

        email_obj = self.emails.filter(is_primary=True).first()  # type: ignore
        return email_obj.is_verified if email_obj else False

    @property
    def phone_verified(self) -> bool:
        """Check if the user's phone number is verified - optimized version"""
        if hasattr(self, "_prefetched_objects_cache") and "phones" in self._prefetched_objects_cache:  # type: ignore
            phones = [p for p in self.phones.all() if p.is_primary]  # type: ignore
            return phones[0].is_verified if phones else False

        phone_obj = self.phones.filter(is_primary=True).first()  # type: ignore
        return phone_obj.is_verified if phone_obj else False

    @property
    def is_deleted(self) -> bool:
        """Check if the user is deleted."""
        # Check if the user is deleted and has a deleted_at timestamp
        status: bool = self.status == UserStatus.DELETED and self.deleted_at is not None
        return status

    def soft_delete(self):
        """Soft delete the user, marking it as deleted."""
        self.status = UserStatus.DELETED
        self.deleted_at = timezone.now()
        self.save()

    def clean(self):
        """Clean the user data by removing whitespace and converting to lowercase."""
        self.username = self.username.lower().strip()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def generate_jwt_token(self):
        """
        Generate JWT tokens (access and refresh) and include additional data
        """
        token = RefreshToken.for_user(self)

        # Add custom claims to the token
        token["username"] = self.username
        token["primaryEmail"] = self.primary_email
        token["primaryPhoneNumber"] = self.primary_phone

        token["emailVerified"] = self.email_verified
        token["phoneVerified"] = self.phone_verified

        token["updatedAt"] = self.updated_at
        token["createdAt"] = self.created_at

        token["role"] = self.role

        return token
