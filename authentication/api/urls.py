from django.urls import path
from .views import LoginAPIView, RegisterView

urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
]
