from django.contrib import admin
from accounts.models import SettingsModel


class SettingsInline(admin.StackedInline):
    model = SettingsModel
    can_delete = False
    verbose_name_plural = "Settings"
    fk_name = "user"
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Appearance", {"fields": ("theme", "language")}),
        ("Security", {"fields": ("email_verified", "email_2fa_enabled")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def get_queryset(self, request):
        """Don't fetch the settings separately - use select_related from parent"""
        return super().get_queryset(request).select_related("user")


@admin.register(SettingsModel)
class SettingsAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "email_verified",
        "last_2fa_setup_at",
        "updated_at",
        "created_at",
    ]
    list_filter = [
        "theme",
        "language",
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
            {
                "fields": (
                    "id",
                    "user",
                )
            },
        ),
        (
            "Appearance",
            {
                "fields": (
                    "theme",
                    "language",
                )
            },
        ),
        (
            "Security",
            {
                "fields": (
                    "primary_2fa_method",
                    "email_verified",
                    "email_2fa_enabled",
                    "require_2fa_for_sensitive_actions",
                )
            },
        ),
        (
            "Important dates",
            {
                "fields": (
                    "last_2fa_setup_at",
                    "updated_at",
                    "created_at",
                )
            },
        ),
    )
