import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.permissions import AllowAny, IsAuthenticated


from authentication.api.v1.serializers import (
    RegisterStep1Serializer,
    RegisterStep2Serializer,
    RegisterStep3Serializer,
    RegisterStep4Serializer,
)

logger = logging.getLogger("app.v1.register_view")


# -----------------------------
# Step 1: Request OTP
# -----------------------------
class RegisterStep1APIView(APIView):
    """
    Handles registration Step 1:
    - Validates email and username
    - Generates and sends OTP
    """

    http_method_names = ["post"]
    permission_classes = [AllowAny]

    throttle_scope = "otp"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request: Request, *args, **kwargs):
        try:
            # Validate data
            serializer = RegisterStep1Serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            # Send OTP
            result = serializer.send_otp(serializer.validated_data)  # type: ignore
            # Extract data
            email = result["email"]  # type: ignore
            # Log and return response
            logger.info(f"OTP sent to {email}")
            return Response(
                data={
                    "status": True,
                    "result": {
                        "email": email,
                    },
                    "message": "OTP sent successfully.",
                },
                status=status.HTTP_200_OK,
            )

        # Handle validation errors
        except ValidationError as ve:
            logger.warning(f"Invalid data in RegisterStep1View: {serializer.errors}")
            return Response(
                {
                    "success": False,
                    "message": "Validation error.",
                    "errors": ve.get_full_details(),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Handle exceptions
        except Exception as e:
            logger.error(f"Exception in RegisterStep1View: {e}")
            return Response(
                data={
                    "success": False,
                    "message": "An error occurred.",
                    "errors": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# -----------------------------
# Step 2: Verify OTP & create user
# -----------------------------
class RegisterStep2APIView(APIView):
    """
    Handles registration Step 2:
    - Validates OTP
    - Marks OTP as used
    - Creates or verifies user
    """

    http_method_names = ["post"]
    permission_classes = [AllowAny]

    throttle_scope = "otp"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request: Request, *args, **kwargs):
        try:
            # Validate data
            serializer = RegisterStep2Serializer(data=request.data)
            if serializer.is_valid():
                # Verify OTP
                result = serializer.verify()  # type: ignore
                # Extract data
                access = result["access"]  # type: ignore
                refresh = result["refresh"]  # type: ignore
                new_user = result["new_user"]  # type: ignore
                # Log and return response
                logger.info(f"User created: {new_user}")
                return Response(
                    data={
                        "status": True,
                        "result": {
                            "verified": True,
                            "new_user": new_user.email,
                            "access": access,
                            "refresh": refresh,
                        },
                        "message": "User created successfully.",
                    },
                    status=status.HTTP_200_OK,
                )
            # Handle invalid data
            logger.warning(f"Invalid data in RegisterStep2View: {serializer.errors}")
            return Response(
                data={
                    "success": False,
                    "message": "Data is invalid.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Handle validation errors
        except ValidationError as ve:
            logger.warning(f"Invalid data in RegisterStep2View: {serializer.errors}")
            return Response(
                {
                    "success": False,
                    "message": "Validation error.",
                    "errors": ve.get_full_details(),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Handle exceptions
        except Exception as e:
            logger.error(f"Exception in RegisterStep2View: {e}")
            return Response(
                data={
                    "success": False,
                    "message": "An error occurred.",
                    "errors": {"detail": str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# -----------------------------
# Step 3: Update profile info (first_name, last_name)
# -----------------------------
class RegisterStep3APIView(APIView):
    """
    Step 3 of registration: update profile info (first_name, last_name).
    User must be authenticated (JWT token from step 2).
    """

    http_method_names = ["patch"]
    permission_classes = [IsAuthenticated]

    throttle_scope = "user"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request: Request, *args, **kwargs):
        try:
            # Validate data
            serializer = RegisterStep3Serializer(
                data=request.data, context={"user": request.user}
            )
            serializer.is_valid(raise_exception=True)
            result = serializer.save()

            # Extract data
            username = result["username"]  # type: ignore
            last_name = result["last_name"]  # type: ignore
            first_name = result["first_name"]  # type: ignore

            # Log and return response
            logger.info(f"Profile information updated: {result}")
            return Response(
                {
                    "success": True,
                    "result": {
                        "username": username,
                        "last_name": last_name,
                        "first_name": first_name,
                    },
                    "message": "Profile information updated successfully.",
                },
                status=status.HTTP_200_OK,
            )
        # Handle validation errors
        except ValidationError as ve:
            logger.warning(f"Invalid data in RegisterStep3View: {serializer.errors}")
            return Response(
                {
                    "success": False,
                    "message": "Validation failed.",
                    "errors": ve.get_full_details(),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Handle exceptions
        except Exception as e:
            logger.error(f"Exception in RegisterStep3View: {e}")
            return Response(
                {
                    "success": False,
                    "message": "Unexpected error.",
                    "errors": {"detail": str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# -----------------------------
# Step 4: Update profile info (password)
# -----------------------------
class RegisterStep4APIView(APIView):
    """
    Step 4 of registration: update user's password.
    User must be authenticated (JWT token from step 2).
    """

    http_method_names = ["patch"]
    permission_classes = [IsAuthenticated]

    throttle_scope = "user"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request: Request, *args, **kwargs):
        try:
            # Validate data
            serializer = RegisterStep4Serializer(
                data=request.data, context={"user": request.user}
            )
            serializer.is_valid(raise_exception=True)
            result = serializer.save()

            # Extract data
            username = result["username"]  # type: ignore
            last_name = result["last_name"]  # type: ignore
            first_name = result["first_name"]  # type: ignore

            # Log and return response
            logger.info(f"Password updated: {result}")
            return Response(
                {
                    "success": True,
                    "result": {
                        "username": username,
                        "last_name": last_name,
                        "first_name": first_name,
                    },
                    "message": "Password updated successfully.",
                },
                status=status.HTTP_200_OK,
            )
        # Handle validation errors
        except ValidationError as ve:
            logger.warning(f"Invalid data in RegisterStep4View: {serializer.errors}")
            return Response(
                {
                    "success": False,
                    "message": "Validation failed.",
                    "errors": ve.get_full_details(),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Handle exceptions
        except Exception as e:
            logger.error(f"Exception in RegisterStep4View: {e}")
            return Response(
                {
                    "success": False,
                    "message": "Unexpected error.",
                    "errors": {"detail": str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
