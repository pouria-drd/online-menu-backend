from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken


from core.constants import OTPType
from .otp_service import OTPService
from accounts.models import UserModel
from accounts.selectors import UserSelectors
from accounts.repositories import UserRepository


class AuthService:
    """Service layer for auth-related business logic."""

    @staticmethod
    def login(email: str, password: str) -> dict:
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

        # Generate JWT tokens
        token = AuthService.generate_jwt_token(user)
        refresh_token = str(token)
        access_token = str(token.access_token)

        UserRepository.update_last_login(user)

        # TODO: Notify user via email service that they have logged in

        return {
            "user": user,
            "access": access_token,
            "refresh": refresh_token,
        }

    @staticmethod
    def send_login_otp(email: str) -> str:
        """
        Send OTP code to user via otp service for login.
        """
        # Generate OTP via otp service
        otp = OTPService.generate(email=email, otp_type=OTPType.LOGIN)
        otp_email = otp.email

        return otp_email

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
