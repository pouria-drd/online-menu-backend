import logging
from rest_framework.request import Request
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle

from authentication.models import OTPModel
from authentication.utils import send_email_verification_code
from authentication.api.serializers import RegisterSerializer

logger = logging.getLogger("register_api")


class RegisterView(generics.CreateAPIView):
    http_method_names = ["post"]
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    # Request rate limit
    throttle_scope = "anon"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request: Request, *args, **kwargs):
        # Call the serializer to validate and create the user
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Save user and profile
            user: User = serializer.save()

            # Send email verification code
            otp_code, otp_obj = OTPModel.create_otp(user)
            send_email_verification_code(user, otp_code)

            logger.info(
                f"User {user.username} registered successfully via register api",
                extra={"username": user.username},
            )

            return Response(
                data={
                    "otp_id": otp_obj.id,
                    "message": f"User {user.username} registered successfully",
                },
                status=status.HTTP_201_CREATED,
            )

        # Return validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
