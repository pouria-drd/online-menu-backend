import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.throttling import ScopedRateThrottle

from authentication.api.v1.serializers import (
    SendOTPLoginSerializer,
    VerifyOTPLoginSerializer,
)

logger = logging.getLogger("app.v1.otp_login_view")


class SendLoginOTPAPIView(APIView):
    http_method_names = ["post"]
    permission_classes = [AllowAny]
    # Request rate limit
    throttle_scope = "anon"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request: Request, *args, **kwargs):
        try:
            # Validate data
            serializer = SendOTPLoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            # Send OTP
            result = serializer.send_otp(serializer.validated_data)  # type: ignore
            # Extract data
            email = result["email"]  # type: ignore
            # Log and return response
            logger.info(f"OTP sent to {email}")
            return Response(
                data={
                    "success": True,
                    "result": {
                        "email": email,
                    },
                    "message": "OTP sent successfully.",
                },
                status=status.HTTP_200_OK,
            )
        # Handle validation errors
        except ValidationError as ve:
            logger.warning(f"Invalid data in OTPLoginAPIView: {serializer.errors}")
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
            logger.error(f"Exception in OTPLoginAPIView: {e}")
            return Response(
                {
                    "success": False,
                    "message": "Unexpected error.",
                    "errors": {"detail": str(e)},
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
            serializer = VerifyOTPLoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            # Verify OTP
            result = serializer.verify()  # type: ignore
            # Extract data
            access = result["access"]  # type: ignore
            refresh = result["refresh"]  # type: ignore
            # Log and return response
            logger.info(f"User logged in via OTP: {result}")
            return Response(
                data={
                    "success": True,
                    "result": {
                        "access": access,
                        "refresh": refresh,
                    },
                    "message": "User logged in successfully.",
                },
                status=status.HTTP_200_OK,
            )
        # Handle validation errors
        except ValidationError as ve:
            logger.warning(
                f"Invalid data in VerifyOTPLoginAPIView: {serializer.errors}"
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
            logger.error(f"Exception in VerifyOTPLoginAPIView: {e}")
            return Response(
                {
                    "success": False,
                    "message": "Unexpected error.",
                    "errors": {"detail": str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
