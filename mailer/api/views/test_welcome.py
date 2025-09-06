from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse

from ...utils import send_welcome_email


def test_welcome(request: HttpRequest):
    User = get_user_model()
    user = User.objects.get(username="admin")
    send_welcome_email(user)
    return HttpResponse("Welcome Email Sent")
