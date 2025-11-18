from django.contrib import admin
from users.models import ProfileModel
from django.utils.html import format_html


# Inline for UserProfile (editable inside User admin)
class ProfileInline(admin.StackedInline):
    extra = 0
    model = ProfileModel
    can_delete = False
    verbose_name_plural = "Profile"
    readonly_fields = ("created_at", "updated_at", "avatar_tag")
    fields = (
        "avatar_tag",
        "avatar",
        "first_name",
        "last_name",
        "created_at",
        "updated_at",
    )

    def avatar_tag(self, obj):
        """Show avatar thumbnail in admin (non-clickable)."""
        if obj.avatar:
            return format_html(
                '<img src="{}" style="height:50px;width:50px;border-radius:50%;" />',
                obj.avatar.url,
            )
        return "-"

    avatar_tag.short_description = "Avatar"

    def get_queryset(self, request):
        """Don't fetch the profile separately - use select_related from parent"""
        return super().get_queryset(request).select_related("user")


# Standalone admin for UserProfile
@admin.register(ProfileModel)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "full_name",
        "updated_at",
        "created_at",
        "avatar_preview",  # show avatar in list view
    ]
    list_filter = [
        "user__status",
        "user__role",
    ]
    search_fields = [
        "user__username",
        "user__email",
        "first_name",
        "last_name",
    ]
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
        "avatar_tag",
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
                    "first_name",
                    "last_name",
                )
            },
        ),
        (
            "Avatar",
            {
                "fields": ("avatar_tag", "avatar"),
            },
        ),
        (
            "Important dates",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    def full_name(self, obj):
        return obj.full_name

    full_name.short_description = "Full Name"

    def avatar_preview(self, obj):
        """Show avatar thumbnail in list_display (non-clickable)."""
        if obj.avatar:
            return format_html(
                '<img src="{}" style="height:30px;width:30px;border-radius:50%;" />',
                obj.avatar.url,
            )
        return "-"

    avatar_preview.short_description = "Avatar"

    def avatar_tag(self, obj):
        """Show avatar thumbnail in admin (non-clickable)."""
        if obj.avatar:
            return format_html(
                '<img src="{}" style="height:50px;width:50px;border-radius:50%;" />',
                obj.avatar.url,
            )
        return "-"

    avatar_tag.short_description = "Avatar"
