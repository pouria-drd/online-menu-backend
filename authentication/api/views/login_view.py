import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import update_last_login
from rest_framework.throttling import ScopedRateThrottle
from authentication.api.serializers import LoginSerializer

logger = logging.getLogger("login_api")


class LoginAPIView(APIView):
    http_method_names = ["post"]
    permission_classes = [AllowAny]
    # Request rate limit
    throttle_scope = "anon"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request: Request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]  # type: ignore

            # Generate token
            token = user.generate_jwt_token()
            refresh_token = str(token)
            access_token = str(token.access_token)

            # update last login and send a security alert to user
            update_last_login(None, user)  # type: ignore

            logger.info(
                f"User {user.username} logged in successfully via login api",
                extra={"username": user.username},
            )

            return Response(
                data={
                    "access": access_token,
                    "refresh": refresh_token,
                },
                status=status.HTTP_200_OK,
            )

        # Handle invalid request
        username = request.data.get("username")  # type: ignore
        logger.info(f"User {username} failed login with invalid credentials")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
