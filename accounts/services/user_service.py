from django.db import transaction
from rest_framework.exceptions import ValidationError


from core.constants import UserRole
from accounts.models import UserModel
from accounts.repositories import UserRepository


class UserService:
    """
    Service layer for user-related business logic.
    Handles:
        - Creating users
        - Creating related objects (profile, settings)
        - Validations for unique email
    """

    @staticmethod
    @transaction.atomic
    def create_user(
        email: str, role: UserRole = UserRole.USER, **extra_fields
    ) -> UserModel:
        """
        Create a fully initialized user:
            - user record
            - profile entry
            - settings entry

        Args:
            email (str): User email address.
            role (UserRole): Assigned user role (default: UserRole.USER).
            extra_fields: Additional fields passed to user creation.

        Returns:
            UserModel: The newly created user instance.

        Raises:
            ValidationError:
                - user_exists: If a user with the given email already exists.
        """

        # Ensure unique email
        existing_user = UserRepository.get_user_by_email(email)
        if existing_user:
            raise ValidationError(
                {"email": "A user with this email already exists."},
                code="user_exists",
            )

        # Create main user
        new_user = UserRepository.create_user(email=email, role=role, **extra_fields)

        # Create related objects (decoupled via repository)
        UserRepository.create_profile(new_user)
        UserRepository.create_settings(new_user)

        new_user.refresh_from_db()
        return new_user

    @staticmethod
    @transaction.atomic
    def update_user(user: UserModel, user_data: dict = {}) -> UserModel:
        """
        Update user, profile, and settings safely.

        Args:
            user (UserModel): The user being updated.
            user_data (dict): Fields for UserModel.

        Returns:
            UserModel: updated user instance.
        """

        # Clean data by removing fields not allowed
        cleaned = UserService._clean_data(
            user_data or {},
            ["id", "status", "role", "email", "password", "created_at", "updated_at"],
        )

        # Update user
        if cleaned:
            UserRepository.update_user(user, **cleaned)
            user.refresh_from_db()

        return user

    @staticmethod
    @transaction.atomic
    def update_user_profile(user: UserModel, profile_data: dict = {}) -> UserModel:
        """
        Update user profile.

        Args:
            user (UserModel): User instance.
            profile_data (dict): Fields for ProfileModel.

        Returns:
            UserModel: Updated user instance.
            ProfileModel: Updated profile instance.
        """

        # Clean data by removing fields not allowed
        cleaned = UserService._clean_data(
            profile_data or {},
            ["id", "user", "created_at", "updated_at"],
        )

        # Update profile
        if cleaned:
            profile = UserRepository.get_user_profile(user)
            UserRepository.update_profile(profile, **cleaned)
            user.refresh_from_db()

        return user

    @staticmethod
    @transaction.atomic
    def update_user_settings(user: UserModel, settings_data: dict = {}) -> UserModel:
        """
        Update user settings.

        Args:
            user (UserModel): User instance.
            settings_data (dict): Fields for SettingsModel.

        Returns:
            UserModel: Updated user instance.
            SettingsModel: Updated settings instance.
        """

        # Clean data by removing fields not allowed
        cleaned = UserService._clean_data(
            settings_data or {},
            ["id", "user", "created_at", "updated_at"],
        )

        # Update settings
        if cleaned:
            settings = UserRepository.get_user_settings(user)
            UserRepository.update_settings(settings, **cleaned)
            user.refresh_from_db()

        return user

    @staticmethod
    @transaction.atomic
    def update_user_password(user: UserModel, password: str) -> UserModel:
        """
        Update user password.

        Args:
            user (UserModel): User instance.
            password (str): New password.

        Returns:
            UserModel: Updated user instance.
        """
        UserRepository.update_user_password(user, password)
        user.refresh_from_db()
        return user

    # -------------------------
    # Internal utility methods
    # -------------------------
    @staticmethod
    def _clean_data(data: dict, disallowed_fields: list[str]) -> dict:
        """
        Clean data from disallowed fields.

        Args:
            data (dict): Data to clean.
            disallowed_fields (list[str]): List of disallowed fields.

        Returns:
            dict: Cleaned data.
        """
        if not data:
            return {}

        return {
            key: value for key, value in data.items() if key not in disallowed_fields
        }
