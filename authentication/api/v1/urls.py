from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView


from .views import LoginAPIView, SendLoginOTPAPIView


urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="login"),
    path("login/send-otp/", SendLoginOTPAPIView.as_view(), name="send-otp"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
]
