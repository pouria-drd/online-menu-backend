from django.urls import path
from .views import TestWelcomeView

urlpatterns = [
    path("test-welcome/", TestWelcomeView.as_view(), name="test_welcome"),
]
