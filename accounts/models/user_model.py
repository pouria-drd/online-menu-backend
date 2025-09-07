import uuid
from accounts.managers import UserManager
from accounts.constants import UserRole, UserStatus, UserVerificationStatus

from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import EmailValidator, RegexValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


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
    # Status for the user (active, banned, deleted)
    status = models.CharField(
        max_length=20,
        choices=UserStatus.choices,
        default=UserStatus.ACTIVE,
        db_index=True,
    )
    # Role for the user (admin, customer, menu owner)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CUSTOMER,
        db_index=True,
    )
    # Verification status for email and phone
    verification_status = models.CharField(
        max_length=20,
        choices=UserVerificationStatus.choices,
        default=UserVerificationStatus.UNVERIFIED,
        db_index=True,
    )
    # Boolean flags for account status
    is_staff = models.BooleanField(default=False)
    # Timestamps for user creation and last update
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Attach the custom manager
    objects = UserManager()

    # Set the USERNAME_FIELD to 'username' for login
    USERNAME_FIELD = "username"
    # Email and Phone number are required for user creation
    REQUIRED_FIELDS = [
        "email",
        "phone_number",
    ]

    class Meta:
        """Meta class for the UserModel."""

        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ("-created_at",)

    def __str__(self):
        """String representation of the user."""
        username = self.username
        return username

    @property
    def is_active(self):
        return self.status == UserStatus.ACTIVE

    @property
    def is_verified(self):
        return self.verification_status == UserVerificationStatus.VERIFIED

    @property
    def is_deleted(self):
        return self.status == UserStatus.DELETED

    def clean(self):
        self.email = self.email.lower().strip()
        self.username = self.username.lower().strip()
        self.phone_number = self.phone_number.strip()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def generate_jwt_token(self):
        """
        Generate JWT tokens (access and refresh) and include additional data
        """
        token = RefreshToken.for_user(self)

        # Add custom claims to the token
        token["email"] = self.email
        token["username"] = self.username
        token["isAdmin"] = self.is_staff

        token["updatedAt"] = self.updated_at
        token["createdAt"] = self.created_at

        token["role"] = self.role
        token["verificationStatus"] = self.verification_status

        return token
