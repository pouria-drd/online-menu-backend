from django.urls import path
from .views import UserRetrieveUpdateView

urlpatterns = [
    path("me/", UserRetrieveUpdateView.as_view(), name="me"),
]
