from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from mailer.utils import send_welcome_email_task
from rest_framework.permissions import IsAdminUser
from rest_framework.throttling import ScopedRateThrottle


class TestWelcomeView(APIView):
    """Class-based view to send a welcome email to admin"""

    http_method_names = ["get"]
    permission_classes = [IsAdminUser]

    throttle_scope = "user"
    throttle_classes = [ScopedRateThrottle]

    def get(self, request: Request, *args, **kwargs):
        User = get_user_model()
        user = User.objects.get(username="admin")
        user_name = user.username
        send_welcome_email_task(user, use_template=False)
        return Response({"message": f"Welcome Email Sent to {user_name}"})
