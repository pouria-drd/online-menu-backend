import uuid
from django.db import models
from django.utils import timezone
from django.core.validators import EmailValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from .user_manager import UserManager
from core.constants import UserRole, UserStatus


class UserModel(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that replaces Django's default user model.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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

    # Attach the custom manager
    objects = UserManager()

    # Set the USERNAME_FIELD to 'email' for login
    USERNAME_FIELD = "email"

    class Meta:
        """Meta class for the UserModel."""

        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        """String representation of the user."""
        return self.email
