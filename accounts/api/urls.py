from django.urls import path
from .views import UserAPIView, UserProfileAPIView, UserSettingsAPIView

urlpatterns = [
    path("me/", UserAPIView.as_view(), name="me"),
    path("me/profile/", UserProfileAPIView.as_view(), name="me-profile"),
    path("me/settings/", UserSettingsAPIView.as_view(), name="me-settings"),
]
