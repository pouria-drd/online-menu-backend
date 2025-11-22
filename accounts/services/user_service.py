from django.db import transaction
from rest_framework.exceptions import ValidationError


from core.constants import UserRole
from accounts.models import UserModel
from accounts.repositories import UserRepository


class UserService:
    """Service layer for user-related business logic."""

    @staticmethod
    @transaction.atomic
    def register_user(
        email: str, role: UserRole = UserRole.USER, **extra_fields
    ) -> UserModel:
        """
        Register a new user with profile and settings in a single transaction.

        Raises:
            ValidationError: If a user with the same email exists.

        Returns:
            UserModel: Newly created user instance.
        """
        # Check if user with email already exists
        if UserRepository.get_user_by_email(email):
            raise ValidationError(
                f"A user with email '{email}' already exists.", code="user_exists"
            )
        # Create user, profile, and settings
        user = UserRepository.create_user(email=email, role=role, **extra_fields)
        UserRepository.create_profile(user)
        UserRepository.create_settings(user)
        return user
