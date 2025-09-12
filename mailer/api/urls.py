from django.urls import path
from django.conf import settings
from .views import TestWelcomeView

base_name = "test"

urlpatterns = []


if settings.DEBUG:
    urlpatterns += [
        path(f"{base_name}-welcome/", TestWelcomeView.as_view(), name="test-welcome"),
    ]
