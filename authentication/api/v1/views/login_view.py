import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.throttling import ScopedRateThrottle

from core.constants import OTPType
from authentication.services import AuthService
from authentication.api.v1.serializers import (
    LoginSerializer,
    SendOTPSerializer,
    VerifyOTPSerializer,
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


class OTPLoginAPIView(APIView):
    http_method_names = ["post"]
    permission_classes = [AllowAny]
    # Request rate limit
    throttle_scope = "otp"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request: Request, *args, **kwargs):
        try:
            # Validate data
            serializer = VerifyOTPSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            # Extract Data
            email = serializer.validated_data["email"]  # type: ignore
            code = serializer.validated_data["code"]  # type: ignore
            # Authenticate user via otp login service
            user, access_token, refresh_token = AuthService.otp_login(
                email=email, code=code
            )
            # Log and return response
            logger.info(f"User {user} logged in successfully via otp login api")
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
