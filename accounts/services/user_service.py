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

        return new_user
