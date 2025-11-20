from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken


from accounts.models import UserModel
from accounts.selectors import UserSelectors
from accounts.repositories import UserRepository


class AuthService:

    @staticmethod
    def login_user(email: str, password: str) -> UserModel:
        """
        Validate login credentials.
        This version is designed for JWT authentication (no session).
        """

        user = UserRepository.get_user_by_email(email)

        if not user:
            raise ValidationError(
                {"form": "Invalid credentials"}, code="invalid_credentials"
            )

        if not UserSelectors.is_active(user):
            raise ValidationError(
                {"form": "Your account is inactive."}, code="inactive"
            )

        if not check_password(password, user.password):
            raise ValidationError(
                {"form": "Invalid credentials"}, code="invalid_credentials"
            )

        UserRepository.update_last_login(user)

        return user

    @staticmethod
    def generate_jwt_token(user: UserModel) -> RefreshToken:
        """
        Generate JWT tokens (access and refresh) and include additional data
        """
        token = RefreshToken.for_user(user)

        # Add custom claims to the token
        token["useId"] = str(user.id)
        token["role"] = user.role

        return token
