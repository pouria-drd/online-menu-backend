from typing import Optional
from django.utils import timezone

from core.constants import UserRole, UserStatus
from accounts.models import UserModel, ProfileModel, SettingsModel


class UserRepository:
    """Repository layer for user-related DB operations."""

    @staticmethod
    def create_user(
        email: str, role: UserRole = UserRole.USER, **extra_fields
    ) -> UserModel:
        """Create a user in the database."""
        return UserModel.objects.create(
            email=email.lower().strip(), role=role, **extra_fields
        )

    @staticmethod
    def create_profile(user: UserModel) -> ProfileModel:
        """Create a profile for the user."""
        return ProfileModel.objects.create(user=user)

    @staticmethod
    def create_settings(user: UserModel) -> SettingsModel:
        """Create settings for the user."""
        return SettingsModel.objects.create(user=user)

    @staticmethod
    def get_user_by_email(email: str) -> Optional[UserModel]:
        """Return user by email, or None."""
        return UserModel.objects.filter(
            email=email.lower().strip(), status=UserStatus.ACTIVE
        ).first()

    @staticmethod
    def update_last_login(user: UserModel):
        """Update the user's last login timestamp."""
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])
