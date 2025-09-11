import logging
from django.db.models import Q
from django.http import HttpRequest
from accounts.models import UserModel
from django.contrib.auth.backends import BaseBackend


logger = logging.getLogger("auth_backend")


class AuthBackend(BaseBackend):
    """
    Custom authentication backend allowing login by both email and username.
    """

    def authenticate(
        self, request: HttpRequest, username=None, password=None, **kwargs
    ):
        if not username or not password:
            return None

        user = None
        try:
            # try email or username lookup
            user = UserModel.objects.get(Q(email=username) | Q(username=username))
        except UserModel.DoesNotExist:
            logger.info(
                f"User {username} failed login with invalid credentials",
                extra={"username": username},
            )
            return None
        except UserModel.MultipleObjectsReturned:

            return None

        if user.check_password(password):
            logger.info(
                f"User {username} logged in successfully",
                extra={"username": username},
            )
            return user
        else:
            logger.info(
                f"User {username} failed login with invalid credentials",
                extra={"username": username},
            )
            return None

    def get_user(self, user_id):
        return UserModel.objects.filter(pk=user_id).first()
