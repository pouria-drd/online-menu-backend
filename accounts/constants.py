from django.db import models


MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2 MB


class UserStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    BANNED = "banned", "Banned"
    DELETED = "deleted", "Deleted"
    INACTIVE = "inactive", "Inactive"


class UserRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    USER = "user", "User"
    MENU_OWNER = "menu_owner", "Menu Owner"


class UserGender(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"
    OTHER = "other", "Other"


class UserTheme(models.TextChoices):
    LIGHT = "light", "Light"
    DARK = "dark", "Dark"
    SYSTEM = "system", "System"


class UserLanguage(models.TextChoices):
    ENGLISH = "en", "English"
    PERSIAN = "fa", "Persian"


class TwoFactorMethod(models.TextChoices):
    """Available 2FA methods"""

    EMAIL = "email", "Email"
    # Future: Add SMS, TOTP, WEBAUTHN, BACKUP_CODES, etc.
    # PHONE = "phone", "Phone"
    # TOTP = "totp", "TOTP (Authenticator App)"
