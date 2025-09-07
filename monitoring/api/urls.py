from django.urls import path
from .views import SystemInfoView

urlpatterns = [
    path("system-info/", SystemInfoView.as_view(), name="system_info_api"),
]
