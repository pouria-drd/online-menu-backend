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
            user, access_token, refresh_token = AuthService.login(
                email=email, password=password
            )
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
    throttle_scope = "otp"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request: Request, *args, **kwargs):
        try:
            # Validate data
            serializer = SendLoginOTPSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            # Extract Data
            email = serializer.validated_data["email"]  # type: ignore
            # Send OTP via auth service
            otp_email = AuthService.send_auth_otp(email=email, otp_type=OTPType.LOGIN)
            # Log and return response
            logger.info(f"OTP sent to {otp_email} via login api")
            return Response(
                data={
                    "success": True,
                    "message": "OTP sent successfully.",
                    "result": {
                        "email": otp_email,
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
    throttle_scope = "otp"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request: Request, *args, **kwargs):
        try:
            # Validate data
            serializer = VerifyLoginOTPSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            # Extract Data
            email = serializer.validated_data["email"]  # type: ignore
            code = serializer.validated_data["code"]  # type: ignore
            # Verify OTP via auth service
            result = AuthService.verify_auth_otp(email=email, code=code)
            # Log and return response
            logger.info(f"OTP verified for {email} via login api")
            return Response(
                data={
                    "success": True,
                    "message": "OTP verified successfully.",
                    "result": result,
                },
                status=status.HTTP_200_OK,
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
