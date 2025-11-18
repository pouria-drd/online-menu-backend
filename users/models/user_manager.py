from users.constants import UserRole, UserStatus
from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """Custom manager for the UserModel, handling user and superuser creation."""

    def create_user(self, username, email, password=None, **extra_fields):
        """Create a new user with the given username, email, and password."""

        if not username:
            raise ValueError("Users must have a username.")

        if not email:
            raise ValueError("Users must have an email.")

        username = username.lower()

        # Normalize email
        email = self.normalize_email(email)

        user = self.model(
            username=username,
            email=email,
            is_superuser=False,
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            **extra_fields
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()  # for OAuth cases

        user.save(using=self._db)

        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """Create a new superuser with the given username, email, and password."""
        user = self.create_user(
            username=username, email=email, password=password, **extra_fields
        )

        # Set the user role to admin and status to active
        user.role = UserRole.ADMIN
        user.status = UserStatus.ACTIVE
        user.is_superuser = True

        user.save(using=self._db)

        return user
