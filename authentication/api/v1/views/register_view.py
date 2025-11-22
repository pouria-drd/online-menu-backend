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
    SendRegisterOTPSerializer,
)

logger = logging.getLogger("app.v1.register_view")


class SendRegisterOTPAPIView(APIView):
    http_method_names = ["post"]
    permission_classes = [AllowAny]
    # Request rate limit
    throttle_scope = "anon"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request: Request, *args, **kwargs):
        try:
            # Validate data
            serializer = SendRegisterOTPSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            # Extract Data
            email = serializer.validated_data["email"]  # type: ignore
            # TODO: Create user via user service
            # Generate OTP via otp service
            otp = OTPService.generate(email=email, otp_type=OTPType.REGISTER)
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
