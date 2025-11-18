import logging
from rest_framework.request import Request
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle

from users.api.v1.serializers import UserSerializer

logger = logging.getLogger(__name__)


class UserRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update the authenticated user's information.
    GET → get current user
    PUT/PATCH → update current user
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    throttle_scope = "user"
    throttle_classes = [ScopedRateThrottle]

    http_method_names = ["get", "put", "patch"]

    def get_object(self):
        """
        Always return the currently authenticated user.
        """
        return self.request.user

    def retrieve(self, request: Request, *args, **kwargs):
        """
        GET /api/v1/users/me/
        """
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request: Request, *args, **kwargs):
        """
        PUT or PATCH /api/v1/users/me/
        """
        partial = kwargs.pop("partial", False)
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        logger.info(f"User updated profile ({user.username})")

        return Response(
            data={
                "message": "User updated successfully.",
            },
            status=status.HTTP_200_OK,
        )
