import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.throttling import ScopedRateThrottle

from authentication.services import AuthService
from accounts.repositories import UserRepository
from authentication.api.v1.serializers import VerifyOTPSerializer

logger = logging.getLogger("app.v1.register_view")


class OTPRegisterAPIView(APIView):
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
            # Create user via auth service
            new_user = AuthService.register(email=email, code=code)
            # Generate JWT tokens
            token = AuthService.generate_jwt_token(new_user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            # Update last login time
            UserRepository.update_last_login(new_user)
            # Log and return response
            logger.info(f"User {new_user} registered successfully via otp register api")
            return Response(
                data={
                    "success": True,
                    "message": "OTP verified successfully.",
                    "result": {
                        "access": access_token,
                        "refresh": refresh_token,
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        # Handle validation errors
        except ValidationError as ve:
            logger.warning(
                f"Invalid data in VerifyRegisterOTPAPIView: {serializer.errors}"
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
            logger.error(f"Exception in VerifyRegisterOTPAPIView: {e}")
            return Response(
                {
                    "success": False,
                    "message": "Unexpected error.",
                    "errors": {"detail": str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
