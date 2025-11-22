from typing import Optional
from django.utils import timezone

from core.constants import UserRole
from accounts.models import UserModel, ProfileModel, SettingsModel


class UserRepository:
    """Repository layer for user-related DB operations."""

    @staticmethod
    def create_user(
        email: str, role: UserRole = UserRole.USER, **extra_fields
    ) -> UserModel:
        """Create a user in the database."""
        normalized_email = email.lower().strip()
        qs = UserModel.objects.create(email=normalized_email, role=role, **extra_fields)
        return qs

    @staticmethod
    def create_profile(user: UserModel) -> ProfileModel:
        """Create a profile for the user."""
        qs = ProfileModel.objects.create(user=user)
        return qs

    @staticmethod
    def create_settings(user: UserModel) -> SettingsModel:
        """Create settings for the user."""
        qs = SettingsModel.objects.create(user=user)
        return qs

    @staticmethod
    def get_user_by_email(email: str) -> Optional[UserModel]:
        """Return user by email, or None."""
        normalized_email = email.lower().strip()
        qs = UserModel.objects.filter(email=normalized_email).first()
        return qs

    @staticmethod
    def update_last_login(user: UserModel):
        """Update the user's last login timestamp."""
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])
