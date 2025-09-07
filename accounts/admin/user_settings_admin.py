from django.contrib import admin
from accounts.models import UserSettings


class UserSettingsInline(admin.StackedInline):
    model = UserSettings
    can_delete = False
    verbose_name_plural = "Settings"
    fk_name = "user"
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Appearance", {"fields": ("theme", "language")}),
        ("Security", {"fields": ("email_otp_login", "phone_otp_login")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "theme",
        "language",
        "email_otp_login",
        "phone_otp_login",
        "updated_at",
        "created_at",
    ]
    list_filter = [
        "theme",
        "language",
        "email_otp_login",
        "phone_otp_login",
    ]
    search_fields = [
        "user__email",
        "user__username",
        "user__phone_number",
    ]
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
    ]
    ordering = [
        "-created_at",
    ]

    fieldsets = (
        (
            "Basic Info",
            {"fields": ("id", "user")},
        ),
        (
            "Appearance",
            {"fields": ("theme", "language")},
        ),
        (
            "Security",
            {"fields": ("email_otp_login", "phone_otp_login")},
        ),
        (
            "Important dates",
            {"fields": ("created_at", "updated_at")},
        ),
    )
