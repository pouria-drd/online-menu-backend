from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle

from accounts.constants import UserStatus
from authentication.models import OTPModel
from authentication.constants import UseCase
from authentication.api.serializers import VerifyEmailSerializer

User = get_user_model()


class VerifyEmailView(APIView):
    """Endpoint for verifying OTP codes"""

    http_method_names = ["post"]
    permission_classes = [AllowAny]
    # Request rate limit
    throttle_scope = "anon"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request: Request, *args, **kwargs):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]  # type: ignore
        code = serializer.validated_data["code"]  # type: ignore

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Get the last active OTP for the user and usecase
        otp = (
            OTPModel.objects.filter(
                user=user, usecase=UseCase.EMAIL_VERIFICATION, used=False
            )
            .order_by("-created_at")
            .first()
        )

        if not otp:
            return Response(
                {
                    "detail": "OTP not found or already used.",
                    "code": "otp_not_found_or_already_used",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # validate
        if otp.validate(code):

            user.status = UserStatus.ACTIVE  # type: ignore
            user.save(update_fields=["status"])

            user_settings = user.settings  # type: ignore
            user_settings.email_verified = True  # type: ignore
            user_settings.save(update_fields=["email_verified"])

            return Response(
                {
                    "detail": "OTP verified successfully.",
                    "code": "otp_verified_successfully",
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "detail": "Invalid or expired OTP.",
                "code": "invalid_or_expired_otp",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
