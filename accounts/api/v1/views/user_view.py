import logging
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.generics import RetrieveUpdateAPIView

from accounts.api.v1.serializers import UserSerializer

logger = logging.getLogger("app.v1.user_view")


class UserView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch"]
    serializer_class = UserSerializer
    throttle_scope = "user"
    throttle_classes = [ScopedRateThrottle]

    def get(self, request: Request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(user)

        logger.info(f"User {user.email} requested their data via UserView")
        return Response(
            {
                "success": True,
                "result": serializer.data,
                "message": "User data retrieved successfully.",
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request: Request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)

        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()

            logger.info(f"User {user.email} updated their data via UserView")
            return Response(
                {
                    "success": True,
                    "result": serializer.data,
                    "message": "User data updated successfully.",
                },
                status=status.HTTP_200_OK,
            )

        except ValidationError as ve:
            logger.warning(
                f"User {user.email} submitted invalid data: {serializer.errors}"
            )
            return Response(
                {
                    "success": False,
                    "message": "Validation error.",
                    "errors": ve.get_full_details(),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            logger.exception(
                f"Unexpected exception in UserView for user {user.email}: {e}"
            )
            return Response(
                {
                    "success": False,
                    "message": "Unexpected error.",
                    "errors": {"detail": str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
