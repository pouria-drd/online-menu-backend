from django.contrib import admin
from apps.accounts.models import SettingsModel


class SettingsInline(admin.StackedInline):
    extra = 0
    model = SettingsModel
    can_delete = False
    verbose_name_plural = "Settings"
    fk_name = "user"
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Appearance", {"fields": ("theme", "language")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def get_queryset(self, request):
        """Don't fetch the settings separately - use select_related from parent"""
        return super().get_queryset(request).select_related("user")


@admin.register(SettingsModel)
class SettingsAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "theme",
        "language",
        "updated_at",
        "created_at",
    ]
    list_filter = [
        "theme",
        "language",
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
            "Important dates",
            {
                "fields": (
                    "updated_at",
                    "created_at",
                )
            },
        ),
    )
