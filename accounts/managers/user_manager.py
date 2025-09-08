from accounts.constants import UserRole, UserStatus
from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """Custom manager for the UserModel, handling user and superuser creation."""

    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Users must have a username")

        username = username.lower()

        user = self.model(username=username, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()  # for OAuth cases
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        user = self.create_user(username=username, password=password, **extra_fields)
        user.role = UserRole.ADMIN
        user.status = UserStatus.ACTIVE
        user.is_superuser = True
        user.save(using=self._db)
        return user
