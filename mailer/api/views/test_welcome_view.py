import logging
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.permissions import AllowAny, IsAdminUser

from mailer.utils import send_welcome_email


logger = logging.getLogger("mailer")


class TestWelcomeView(APIView):
    """Class-based view to send a welcome email to admin"""

    http_method_names = ["get"]
    permission_classes = [AllowAny if settings.DEBUG else IsAdminUser]

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "anon" if settings.DEBUG else "user"

    def get(self, request: Request, *args, **kwargs):
        User = get_user_model()
        user = User.objects.get(username="admin")
        user_name = user.username
        send_welcome_email(user)
        logger.info(f"Welcome email sent to {user_name}")
        return Response({"message": f"Welcome Email Sent to {user_name}"})
