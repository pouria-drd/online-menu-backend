from django.db import models

from online_menu_backend.env import ENV_MAX_AVATAR_SIZE_MB


MAX_AVATAR_SIZE_MB = ENV_MAX_AVATAR_SIZE_MB
MAX_AVATAR_SIZE = MAX_AVATAR_SIZE_MB * 1024 * 1024  # 2 MB
VALID_AVATAR_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]


class UserStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    BANNED = "banned", "Banned"
    DELETED = "deleted", "Deleted"
    INACTIVE = "inactive", "Inactive"


class UserRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    USER = "user", "User"


class UserTheme(models.TextChoices):
    LIGHT = "light", "Light"
    DARK = "dark", "Dark"
    SYSTEM = "system", "System"


class UserLanguage(models.TextChoices):
    ENGLISH = "en", "English"
    PERSIAN = "fa", "Persian"
