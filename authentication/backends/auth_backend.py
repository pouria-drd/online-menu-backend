import logging
from django.db.models import Q
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import update_last_login

UserModel = get_user_model()

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
            logger.error(
                f"Multiple users with same username or email found: {username}",
                extra={"username": username},
            )
            return None

        if user.check_password(password) and user.is_active:
            # update last login and send a security alert to user
            update_last_login(None, user)  # type: ignore
            user_name = user.username
            logger.info(
                f"User {user_name} logged in successfully",
                extra={"username": user_name},
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
