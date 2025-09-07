import re
import logging
from accounts.models import UserModel
from accounts.utils import normalize_phone

from django.db.models import Q
from django.http import HttpRequest
from django.contrib.auth.backends import BaseBackend


logger = logging.getLogger("auth_backend")


class AuthBackend(BaseBackend):
    """
    Custom authentication backend allowing login by email, username, or phone number.
    Phone numbers are normalized to handle Iranian formats.
    """

    def authenticate(
        self, request: HttpRequest, username=None, password=None, **kwargs
    ):
        if not username or not password:
            return None

        username = username.strip()

        # Determine if username looks like a phone number (digits or Persian digits)
        if re.search(r"[0-9۰-۹]", username):
            normalized_phone = normalize_phone(username)
        else:
            normalized_phone = None

        # Normalize email and username to lowercase
        username_lower = username.lower()

        user = None
        try:
            if normalized_phone:
                # Try phone lookup first if phone-like input
                user = UserModel.objects.get(phone_number=normalized_phone)
            else:
                # Otherwise, try email or username lookup
                user = UserModel.objects.get(
                    Q(email=username_lower) | Q(username=username_lower)
                )
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
