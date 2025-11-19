from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView


from .views import (
    LoginAPIView,
    SendLoginOTPAPIView,
    VerifyLoginOTPAPIView,
    RegisterStep1APIView,
    RegisterStep2APIView,
    RegisterStep3APIView,
    RegisterStep4APIView,
)


urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="login"),
    path("login/send-otp/", SendLoginOTPAPIView.as_view(), name="send-login-otp"),
    path("login/verify-otp/", VerifyLoginOTPAPIView.as_view(), name="verify-login-otp"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("register/step1/", RegisterStep1APIView.as_view(), name="register-step1"),
    path("register/step2/", RegisterStep2APIView.as_view(), name="register-step2"),
    path("register/step3/", RegisterStep3APIView.as_view(), name="register-step3"),
    path("register/step4/", RegisterStep4APIView.as_view(), name="register-step4"),
]
