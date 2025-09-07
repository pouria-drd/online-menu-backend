import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.generics import RetrieveUpdateAPIView
from accounts.api.serializers import (
    UserSerializer,
    UserProfileSerializer,
    UserSettingsSerializer,
)

logger = logging.getLogger("user_api")


class UserAPIView(RetrieveUpdateAPIView):
    """API endpoint for user profile"""

    serializer_class = UserSerializer

    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "put", "patch"]

    throttle_scope = "user"
    throttle_classes = [ScopedRateThrottle]

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        logger.info(f"User {request.user.username} requested their info")
        return super().get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        logger.info(f"User {request.user.username} updated their info")
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        logger.info(f"User {request.user.username} updated their info")
        return super().patch(request, *args, **kwargs)


class UserProfileAPIView(RetrieveUpdateAPIView):
    """API endpoint for user profile"""

    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    http_method_names = ["get", "put", "patch"]

    throttle_scope = "user"
    throttle_classes = [ScopedRateThrottle]

    def get_object(self):
        return self.request.user.profile  # type: ignore

    def get(self, request, *args, **kwargs):
        logger.info(f"User {request.user.username} requested their profile")
        return super().get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        logger.info(f"User {request.user.username} updated their profile")
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        logger.info(f"User {request.user.username} updated their profile")
        return super().patch(request, *args, **kwargs)


class UserSettingsAPIView(RetrieveUpdateAPIView):
    """API endpoint for user settings"""

    permission_classes = [IsAuthenticated]
    serializer_class = UserSettingsSerializer
    http_method_names = ["get", "put", "patch"]

    throttle_scope = "user"
    throttle_classes = [ScopedRateThrottle]

    def get_object(self):
        return self.request.user.settings  # type: ignore

    def get(self, request, *args, **kwargs):
        logger.info(f"User {request.user.username} requested their settings")
        return super().get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        logger.info(f"User {request.user.username} updated their settings")
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        logger.info(f"User {request.user.username} updated their settings")
        return super().patch(request, *args, **kwargs)
