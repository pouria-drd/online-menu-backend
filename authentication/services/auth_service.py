from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken


from .otp_service import OTPService
from core.constants import OTPType, UserRole

from accounts.models import UserModel
from accounts.services import UserService
from accounts.selectors import UserSelectors
from accounts.repositories import UserRepository


class AuthService:
    """
    Service layer for authentication logic.
    Handles:
    - Register user (OTP-based)
    - Login user (OTP and password based)
    - Token generation
    """

    @staticmethod
    def register(email: str, code: str) -> UserModel:
        """
        Finalize user registration after OTP verification.

        Args:
            email (str): User email.
            code (str): OTP code.

        Returns:
            UserModel: Newly created user.

        Raises:
            ValidationError: When OTP is invalid or user already exists.
        """
        # Check OTP validity
        is_valid = OTPService.verify_otp(
            email=email, code=code, otp_type=OTPType.REGISTER
        )

        if not is_valid:
            raise ValidationError({"form": "Invalid OTP."}, code="invalid_otp")

        # Create new user via user service
        user = UserService.create_user(email=email, role=UserRole.USER)

        # TODO: Notify user via email service that they have registered

        return user

    @staticmethod
    def login(email: str, password: str) -> tuple:
        """
        Login user with password and return JWT tokens.

        Args:
            email (str): User email.
            password (str): Raw password.

        Returns:
            tuple: user instance + access + refresh token.

        Raises:
            ValidationError: If credentials are invalid or account inactive.
        """
        # Try to get user by email
        user = UserRepository.get_user_by_email(email)
        if not user:
            raise ValidationError(
                {"form": "Invalid credentials"}, code="invalid_credentials"
            )
        # Check if password is correct
        is_correct = check_password(password, user.password)
        if not is_correct:
            raise ValidationError(
                {"form": "Invalid credentials"}, code="invalid_credentials"
            )
        # Check if user is active
        is_active = UserSelectors.is_active(user)
        if not is_active:
            raise ValidationError(
                {"form": "Your account is inactive."}, code="inactive"
            )
        # Generate JWT tokens
        token = AuthService.generate_jwt_token(user)
        refresh_token = str(token)
        access_token = str(token.access_token)
        # Update last login time
        UserRepository.update_last_login(user)

        # TODO: Notify user via email service that they have logged in

        return user, access_token, refresh_token

    @staticmethod
    def otp_login(email: str, code: str) -> tuple:
        """
        Login user with OTP and return JWT tokens.

        Args:
            email (str): User email.
            code (str): OTP code.

        Returns:
            tuple: user instance + access + refresh token.

        Raises:
            ValidationError: If credentials are invalid or account inactive.
        """
        # Check OTP validity
        is_valid = OTPService.verify_otp(email=email, code=code, otp_type=OTPType.LOGIN)
        if not is_valid:
            raise ValidationError({"form": "Invalid OTP."}, code="invalid_otp")

        # Try to get user by email
        user = UserRepository.get_user_by_email(email)
        if not user:
            raise ValidationError({"form": "User not found."}, code="user_not_found")

        # Check if user is active
        is_active = UserSelectors.is_active(user)
        if not is_active:
            raise ValidationError(
                {"form": "Your account is inactive."}, code="inactive"
            )

        # Generate JWT tokens
        token = AuthService.generate_jwt_token(user)
        refresh_token = str(token)
        access_token = str(token.access_token)
        # Update last login time
        UserRepository.update_last_login(user)

        # TODO: Notify user via email service that they have logged in

        return user, access_token, refresh_token

    @staticmethod
    def send_auth_otp(email: str, otp_type: OTPType) -> str:
        """
        Send an OTP to email for login/register.

        For register:
            - Ensures no user exists.
        For login:
            - Ensures user already exists.

        Returns:
            str: email the OTP was sent to.

        Raises:
            ValidationError: if otp_type rules are violated.
        """
        # Try to get user by email
        existing_user = UserRepository.get_user_by_email(email)

        # Check otp_type rules
        if otp_type == OTPType.REGISTER:
            # Ensure no user exists
            if existing_user:
                raise ValidationError(
                    {"email": "User already exists."}, code="user_exists"
                )
        # Check otp_type rules
        elif otp_type == OTPType.LOGIN:
            # Ensure user exists
            if not existing_user:
                raise ValidationError(
                    {"email": "User does not exist."}, code="user_not_found"
                )
        # Generate OTP via otp service
        otp = OTPService.send_otp(email=email, otp_type=otp_type)
        return otp.email

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
