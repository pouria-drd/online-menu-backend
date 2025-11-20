import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.throttling import ScopedRateThrottle

from accounts.repositories import UserRepository
from core.constants import OTPType
from authentication.services import AuthService, OTPService
from authentication.api.v1.serializers import (
    LoginSerializer,
    SendLoginOTPSerializer,
    VerifyLoginOTPSerializer,
)

logger = logging.getLogger("app.v1.login_view")


class LoginAPIView(APIView):
    http_method_names = ["post"]
    permission_classes = [AllowAny]
    # Request rate limit
    throttle_scope = "anon"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request: Request, *args, **kwargs):
        try:
            # Validate data
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            # Extract Data
            email = serializer.validated_data["email"]  # type: ignore
            password = serializer.validated_data["password"]  # type: ignore
            # Authenticate user via auth service
            user = AuthService.login_user(email=email, password=password)
            # Generate JWT tokens
            token = AuthService.generate_jwt_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            # Log and return response
            logger.info(f"User {user} logged in successfully via login api")
            return Response(
                data={
                    "success": True,
                    "result": {
                        "access": access_token,
                        "refresh": refresh_token,
                    },
                    "message": "User logged in successfully.",
                },
                status=status.HTTP_200_OK,
            )
        # Handle validation errors
        except ValidationError as ve:
            logger.warning(f"Invalid data in LoginAPIView: {serializer.errors}")
            return Response(
                {
                    "success": False,
                    "message": "Validation error.",
                    "errors": ve.get_full_details(),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Handle exceptions
        except Exception as e:
            logger.error(f"Exception in LoginAPIView: {e}")
            return Response(
                {
                    "success": False,
                    "message": "Unexpected error.",
                    "errors": {"detail": str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SendLoginOTPAPIView(APIView):
    http_method_names = ["post"]
    permission_classes = [AllowAny]
    # Request rate limit
    throttle_scope = "anon"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request: Request, *args, **kwargs):
        try:
            # Validate data
            serializer = SendLoginOTPSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            # Extract Data
            email = serializer.validated_data["email"]  # type: ignore
            # Generate OTP via otp service
            otp = OTPService.generate(email=email, otp_type=OTPType.LOGIN)
            # Log and return response
            logger.info(f"OTP sent to {otp.email} via login api")
            return Response(
                data={
                    "success": True,
                    "message": "OTP sent successfully.",
                    "result": {
                        "email": otp.email,
                    },
                },
                status=status.HTTP_200_OK,
            )
        # Handle validation errors
        except ValidationError as ve:
            logger.warning(f"Invalid data in SendLoginOTPAPIView: {serializer.errors}")
            return Response(
                {
                    "success": False,
                    "message": "Validation error.",
                    "errors": ve.get_full_details(),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Handle exceptions
        except Exception as e:
            logger.error(f"Exception in SendLoginOTPAPIView: {e}")
            return Response(
                {
                    "success": False,
                    "message": "Unexpected error.",
                    "errors": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class VerifyLoginOTPAPIView(APIView):
    http_method_names = ["post"]
    permission_classes = [AllowAny]
    # Request rate limit
    throttle_scope = "anon"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request: Request, *args, **kwargs):
        try:
            # Validate data
            serializer = VerifyLoginOTPSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            # Extract Data
            email = serializer.validated_data["email"]  # type: ignore
            code = serializer.validated_data["code"]  # type: ignore
            # Check if OTP is valid
            valid = OTPService.verify(email=email, code=code)
            # if is valid, return success response
            if valid:
                user = UserRepository.get_user_by_email(email)
                # if user is not None, return success response
                if user:
                    # Update last login time
                    UserRepository.update_last_login(user)
                    # Generate JWT tokens
                    token = AuthService.generate_jwt_token(user)
                    refresh_token = str(token)
                    access_token = str(token.access_token)
                    # Log and return response
                    logger.info(f"OTP verified for {email} via login api")
                    return Response(
                        data={
                            "success": True,
                            "message": "OTP verified successfully.",
                            "result": {
                                "access": access_token,
                                "refresh": refresh_token,
                            },
                        },
                        status=status.HTTP_200_OK,
                    )
                # if user is None, return error response
                else:
                    logger.warning(f"User not found for {email} via login api")
                    return Response(
                        data={
                            "success": False,
                            "message": "User not found.",
                            "errors": {
                                "form": {
                                    "message": "User not found.",
                                    "code": "user_not_found",
                                }
                            },
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )
            # if not valid, return error response
            else:
                logger.warning(f"Invalid OTP for {email} via login api")
                return Response(
                    data={
                        "success": False,
                        "message": "Invalid OTP.",
                        "errors": {
                            "form": {"message": "Invalid OTP.", "code": "invalid_otp"}
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Handle validation errors
        except ValidationError as ve:
            logger.warning(
                f"Invalid data in VerifyLoginOTPAPIView: {serializer.errors}"
            )
            return Response(
                {
                    "success": False,
                    "message": "Validation error.",
                    "errors": ve.get_full_details(),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Handle exceptions
        except Exception as e:
            logger.error(f"Exception in VerifyLoginOTPAPIView: {e}")
            return Response(
                {
                    "success": False,
                    "message": "Unexpected error.",
                    "errors": {"detail": str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
