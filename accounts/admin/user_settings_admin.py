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
        ("Security", {"fields": ("email_2fa", "email_verified")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def get_queryset(self, request):
        """Don't fetch the settings separately - use select_related from parent"""
        return super().get_queryset(request).select_related("user")


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "theme",
        "language",
        "email_2fa",
        "email_verified",
        "updated_at",
        "created_at",
    ]
    list_filter = [
        "theme",
        "language",
        "email_2fa",
        "email_verified",
    ]
    search_fields = [
        "user__email",
        "user__username",
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
            {"fields": ("email_2fa", "email_verified")},
        ),
        (
            "Important dates",
            {"fields": ("created_at", "updated_at")},
        ),
    )
