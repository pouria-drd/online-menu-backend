from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView


from .views import (
    # Login
    LoginAPIView,
    OTPLoginAPIView,
    # Register
    OTPRegisterAPIView,
    # OTP
    SendOTPAPIView,
)


urlpatterns = [
    # Login
    path("login/", LoginAPIView.as_view(), name="login"),
    # Refresh
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    # OTP
    path("otp/send/", SendOTPAPIView.as_view(), name="send-otp"),
    path("otp/login/", OTPLoginAPIView.as_view(), name="otp-login"),
    path("otp/register/", OTPRegisterAPIView.as_view(), name="otp-register"),
]
