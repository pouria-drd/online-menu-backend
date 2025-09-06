from django.urls import path
from .views import test_welcome

urlpatterns = [
    path("test_welcome/", test_welcome, name="test_welcome"),
]
