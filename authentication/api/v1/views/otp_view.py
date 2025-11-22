import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.throttling import ScopedRateThrottle

from authentication.services import AuthService
from authentication.api.v1.serializers import SendOTPSerializer

logger = logging.getLogger("app.v1.otp_view")


class SendOTPAPIView(APIView):
    http_method_names = ["post"]
    permission_classes = [AllowAny]
    # Request rate limit
    throttle_scope = "otp"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request: Request, *args, **kwargs):
        try:
            # Validate data
            serializer = SendOTPSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            # Extract Data
            otp_type = serializer.validated_data["otp_type"]  # type: ignore
            validated_email = serializer.validated_data["email"]  # type: ignore
            # Send OTP via auth service
            otp_email = AuthService.send_auth_otp(
                email=validated_email, otp_type=otp_type
            )
            # Log and return response
            logger.info(f"OTP sent to {otp_email} via register api")
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
