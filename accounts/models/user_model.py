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
                message="Only lowercase letters, numbers, and underscores are allowed and must be at most 25 characters long.",
                code="invalid_username",
            )
        ],  # Apply username validator
        help_text="Required. 25 characters or fewer. Letters, digits, and _ only.",
    )
    # Email is required for user creation and must be unique
    email = models.EmailField(
        unique=True,
        validators=[
            EmailValidator(
                message="Enter a valid email address.",
                code="invalid_email",
            )
        ],
        help_text="Enter a valid email address.",
    )
    # Status for the user (active, banned, deleted)
    status = models.CharField(
        max_length=20,
        choices=UserStatus.choices,
        default=UserStatus.INACTIVE,
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
    def is_deleted(self) -> bool:
        """Check if the user is deleted."""
        # Check if the user is deleted and has a deleted_at timestamp
        status: bool = self.status == UserStatus.DELETED and self.deleted_at is not None
        return status

    # Attach the custom manager
    objects = UserManager()

    # Set the USERNAME_FIELD to 'username' for login
    USERNAME_FIELD = "username"
    # Email is required for user creation
    REQUIRED_FIELDS = ["email"]

    class Meta:
        """Meta class for the UserModel."""

        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        """String representation of the user."""
        username = self.username
        return username

    def soft_delete(self):
        """Soft delete the user, marking it as deleted."""
        self.status = UserStatus.DELETED
        self.deleted_at = timezone.now()
        self.save()

    def clean(self):
        self.email = self.email.lower().strip()
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
        token["id"] = str(self.id)
        token["role"] = self.role
        token["email"] = self.email
        token["username"] = self.username

        token["createdAt"] = self.created_at.isoformat()
        token["updatedAt"] = self.updated_at.isoformat()

        return token
