from django.urls import path
from .views import system_info_api

urlpatterns = [
    path("system-info/", system_info_api, name="system_info_api"),
]
