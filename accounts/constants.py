from django.db import models


class UserStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    BANNED = "banned", "Banned"
    DELETED = "deleted", "Deleted"
    INACTIVE = "inactive", "Inactive"


class UserRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    CUSTOMER = "customer", "Customer"
    MENU_OWNER = "menu_owner", "Menu Owner"


class UserVerificationStatus(models.TextChoices):
    UNVERIFIED = "unverified", "Unverified"
    EMAIL_VERIFIED = "email_verified", "Email Verified"
    PHONE_VERIFIED = "phone_verified", "Phone Verified"
    VERIFIED = "verified", "Fully Verified"
