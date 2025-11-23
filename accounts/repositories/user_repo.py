from typing import Optional
from django.utils import timezone

from core.constants import UserRole
from accounts.models import UserModel, ProfileModel, SettingsModel


class UserRepository:
    """
    Repository layer responsible for database operations related to Users,
    Profiles, and Settings.

    This layer isolates the ORM logic from business logic (services).
    """

    # ----------------------------------------------------------------------
    # CREATE METHODS
    # ----------------------------------------------------------------------

    @staticmethod
    def create_user(
        email: str, role: UserRole = UserRole.USER, **extra_fields
    ) -> UserModel:
        """
        Create and return a new user.

        Args:
            email (str): Email of the user (will be normalized).
            role (UserRole): User role enum value.
            extra_fields: Additional fields to pass to the User model.

        Returns:
            UserModel: The newly created user instance.
        """
        normalized_email = email.lower().strip()
        user = UserModel.objects.create(
            email=normalized_email, role=role, **extra_fields
        )
        return user

    @staticmethod
    def create_profile(user: UserModel) -> ProfileModel:
        """
        Create a profile associated with a user.

        Args:
            user (UserModel): The user instance.

        Returns:
            ProfileModel: The created profile.
        """
        profile = ProfileModel.objects.create(user=user)
        return profile

    @staticmethod
    def create_settings(user: UserModel) -> SettingsModel:
        """
        Create settings associated with a user.

        Args:
            user (UserModel): The user instance.

        Returns:
            SettingsModel: The created settings object.
        """
        settings = SettingsModel.objects.create(user=user)
        return settings

    # ----------------------------------------------------------------------
    # UPDATE METHODS
    # ----------------------------------------------------------------------

    @staticmethod
    def update_user(user: UserModel, **fields) -> UserModel:
        """
        Update user fields and persist changes.

        Args:
            user (UserModel): User instance to update.
            fields: Fields to update.

        Returns:
            UserModel: Updated user instance.
        """
        for key, value in fields.items():
            setattr(user, key, value)

        user.save(update_fields=list(fields.keys()))
        return user

    @staticmethod
    def update_profile(profile: ProfileModel, **fields) -> ProfileModel:
        """
        Update profile fields and persist changes.

        Args:
            profile (ProfileModel): Profile instance to update.
            fields: Fields to update.

        Returns:
            ProfileModel: Updated profile instance.
        """
        for key, value in fields.items():
            setattr(profile, key, value)

        profile.save(update_fields=list(fields.keys()))
        return profile

    @staticmethod
    def update_settings(settings: SettingsModel, **fields) -> SettingsModel:
        """
        Update settings fields and persist changes.

        Args:
            settings (SettingsModel): Settings instance to update.
            fields: Fields to update.

        Returns:
            SettingsModel: Updated settings instance.
        """
        for key, value in fields.items():
            setattr(settings, key, value)

        settings.save(update_fields=list(fields.keys()))
        return settings

    @staticmethod
    def update_user_password(user: UserModel, password: str) -> UserModel:
        """
        Update user password.

        Args:
            user (UserModel): User instance.
            password (str): New password.

        Returns:
            UserModel: Updated user instance.
        """
        user.set_password(password)
        user.save(update_fields=["password"])
        return user

    # ----------------------------------------------------------------------
    # GETTERS
    # ----------------------------------------------------------------------

    @staticmethod
    def get_user_by_email(email: str) -> Optional[UserModel]:
        """
        Retrieve a user by email.

        Args:
            email (str): Email to search for.

        Returns:
            Optional[UserModel]: User instance if found, else None.
        """
        normalized_email = email.lower().strip()
        user = UserModel.objects.filter(email=normalized_email).first()
        return user

    @staticmethod
    def get_user_profile(user: UserModel) -> ProfileModel:
        """
        Retrieve the user's profile.

        Args:
            user (UserModel): User instance.

        Returns:
            ProfileModel: The user's profile.
        """

        profile = ProfileModel.objects.get(user=user)
        return profile

    @staticmethod
    def get_user_settings(user: UserModel) -> SettingsModel:
        """
        Retrieve the user's settings.

        Args:
            user (UserModel): User instance.

        Returns:
            SettingsModel: The user's settings.
        """

        settings = SettingsModel.objects.get(user=user)
        return settings

    # ----------------------------------------------------------------------
    # UTILITIES
    # ----------------------------------------------------------------------

    @staticmethod
    def update_last_login(user: UserModel) -> None:
        """
        Update the last login timestamp for a user.

        Args:
            user (UserModel): User to update.
        """
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])
