import logging
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.permissions import AllowAny, IsAdminUser

from monitoring.utils import get_system_info

logger = logging.getLogger("monitoring")


class SystemInfoView(APIView):
    """Class-based API view for system information"""

    http_method_names = ["get"]
    permission_classes = [AllowAny if settings.DEBUG else IsAdminUser]

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "anon" if settings.DEBUG else "user"

    def get(self, request: Request, *args, **kwargs):
        system_info = get_system_info()
        logger.info("API request received for system info")
        return Response(system_info)
