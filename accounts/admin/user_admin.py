from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import UserModel

# from .profile_admin import ProfileInline
# from .settings_admin import SettingsInline


# @admin.action(description="Soft-delete selected users")
# def soft_delete_users(modeladmin, request, queryset):
#     from users.services import UserService

#     for user in queryset:
#         UserService.soft_delete_user(user)


@admin.register(UserModel)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for UserModel"""

    # inlines = [
    #     ProfileInline,
    #     SettingsInline,
    # ]

    # actions = [soft_delete_users]

    list_per_page = 25
    # list_max_show_all = 100

    # All the previous optimization code here...
    list_display = [
        "email",
        "status",
        "role",
        "is_staff",
        # "is_superuser",
        "last_login",
        # "updated_at",
        "created_at",
    ]

    search_fields = [
        "email",
    ]

    list_filter = [
        "role",
        "status",
        "groups",
        "is_superuser",
    ]

    ordering = [
        "-created_at",
        # "email",
    ]

    readonly_fields = [
        "id",
        "last_login",
        "updated_at",
        "created_at",
        "is_superuser",
    ]

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "role",
                    "status",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    fieldsets = (
        (
            "Basic Info",
            {
                "fields": (
                    "id",
                    "email",
                    "password",
                )
            },
        ),
        (
            "Role & Status",
            {
                "fields": (
                    "role",
                    "status",
                    "is_superuser",
                )
            },
        ),
        (
            "Important Dates",
            {"fields": ("last_login", "created_at", "updated_at")},
        ),
        (
            "Permissions",
            {"classes": ("collapse",), "fields": ("groups", "user_permissions")},
        ),
    )
