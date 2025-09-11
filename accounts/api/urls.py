from django.urls import path
from .views import UserAPIView, ProfileAPIView, SettingsAPIView

base = "user"

urlpatterns = [
    path(f"{base}/", UserAPIView.as_view(), name=f"{base}"),
    path(f"{base}/profile/", ProfileAPIView.as_view(), name=f"{base}-profile"),
    path(f"{base}/settings/", SettingsAPIView.as_view(), name=f"{base}-settings"),
]
