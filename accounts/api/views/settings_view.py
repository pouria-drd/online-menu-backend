import logging
from accounts.api.serializers import SettingsSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.generics import RetrieveUpdateAPIView


logger = logging.getLogger("user_api")


class SettingsAPIView(RetrieveUpdateAPIView):
    """API endpoint for user settings"""

    permission_classes = [IsAuthenticated]
    serializer_class = SettingsSerializer
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
