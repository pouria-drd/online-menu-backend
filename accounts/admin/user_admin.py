from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.utils.formats import date_format
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import UserModel
from .user_profile_admin import UserProfileInline
from .user_settings_admin import UserSettingsInline
from accounts.constants import UserStatus, UserVerificationStatus


@admin.action(description="Mark selected users as fully verified")
def mark_as_verified(modeladmin, request, queryset):
    queryset.update(verification_status=UserVerificationStatus.VERIFIED)


@admin.action(description="Soft-delete selected users")
def soft_delete_users(modeladmin, request, queryset):
    for user in queryset:
        user.soft_delete()


@admin.register(UserModel)
class UserAdmin(BaseUserAdmin):
    """Advanced admin configuration for UserModel with Groups & Permissions"""

    inlines = [
        UserProfileInline,
        UserSettingsInline,
    ]
    # Fields to display in the list view
    list_display = [
        "email",
        "username",
        "phone_number",
        "role",
        "is_staff",
        "is_superuser",
        "status_verification_info",
        "last_login",
        "updated_at",
        "created_at",
    ]

    # Searchable fields
    search_fields = [
        "username",
        "email",
        "phone_number",
    ]

    # Sidebar filters
    list_filter = [
        "role",
        "status",
        "verification_status",
        "is_staff",
        "is_superuser",
        "groups",
    ]

    # Default ordering
    ordering = [
        "-created_at",
    ]

    # Read-only fields
    readonly_fields = [
        "id",
        "last_login",
        "created_at",
        "updated_at",
        "deleted_at",
    ]

    # Custom actions
    actions = [mark_as_verified, soft_delete_users]

    # Fieldsets for the admin detail page
    fieldsets = (
        (
            "Basic Info",
            {
                "fields": (
                    "id",
                    "username",
                    "email",
                    "phone_number",
                    "password",
                )
            },
        ),
        (
            "Permissions & Roles",
            {
                "classes": ("collapse",),
                "fields": (
                    "role",
                    "status",
                    "verification_status",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            "Important dates",
            {
                "classes": ("collapse",),
                "fields": ("last_login", "created_at", "updated_at", "deleted_at"),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "phone_number",
                    "password1",
                    "password2",
                    "role",
                    "status",
                    "verification_status",
                ),
            },
        ),
    )

    def user_role_info(self, obj):
        # Badge for role
        role_colors = {
            "admin": "#1762b8",
            "customer": "#28a745",
            "menu_owner": "#fd7e14",
        }
        role_color = role_colors.get(obj.role, "#6c757d")
        role_badge = format_html(
            '<span style="background-color:{}; color:white; padding:2px 6px; border-radius:4px; font-size:11px;">{}</span>',
            role_color,
            obj.role,
        )

        # Badge for is_staff
        staff_text = "Staff" if obj.is_staff else "Not Staff"
        staff_color = "#28a745" if obj.is_staff else "#6c757d"
        staff_badge = format_html(
            '<span style="background-color:{}; color:white; padding:2px 6px; border-radius:4px; font-size:11px;">{}</span>',
            staff_color,
            staff_text,
        )

        # Badge for is_superuser
        super_text = "Superuser" if obj.is_superuser else "Not Superuser"
        super_color = "#28a745" if obj.is_superuser else "#6c757d"
        super_badge = format_html(
            '<span style="background-color:{}; color:white; padding:2px 6px; border-radius:4px; font-size:11px;">{}</span>',
            super_color,
            super_text,
        )

        return format_html("{} {} {}", role_badge, staff_badge, super_badge)

    user_role_info.short_description = "User Role Info"

    def status_verification_info(self, obj):
        # Badge for Status
        status_colors = {
            UserStatus.ACTIVE: "#28a745",
            UserStatus.INACTIVE: "#fd7e14",
            UserStatus.BANNED: "#dc3545",
            UserStatus.DELETED: "#6c757d",
        }
        status_badge = format_html(
            '<span style="background-color:{}; color:white; padding:2px 6px; border-radius:4px; font-size:11px; margin-right:4px;">{}</span>',
            status_colors.get(obj.status, "#343a40"),
            obj.get_status_display(),
        )

        # Badge for Verification Status
        verification_colors = {
            UserVerificationStatus.UNVERIFIED: "#6c757d",
            UserVerificationStatus.EMAIL_VERIFIED: "#1762b8",
            UserVerificationStatus.PHONE_VERIFIED: "#ddac19",
            UserVerificationStatus.VERIFIED: "#28a745",
        }
        verification_badge = format_html(
            '<span style="background-color:{}; color:white; padding:2px 6px; border-radius:4px; font-size:11px;">{}</span>',
            verification_colors.get(obj.verification_status, "#343a40"),
            obj.get_verification_status_display(),
        )

        return format_html("{} {}", status_badge, verification_badge)

    status_verification_info.short_description = "Status / Verification"

    def status_colored(self, obj):
        badge_styles = {
            UserStatus.ACTIVE: "background-color: #28a745; color: white; padding: 2px 6px; border-radius: 6px;",
            UserStatus.INACTIVE: "background-color: #fd7e14; color: white; padding: 2px 6px; border-radius: 6px;",
            UserStatus.BANNED: "background-color: #dc3545; color: white; padding: 2px 6px; border-radius: 6px;",
            UserStatus.DELETED: "background-color: #6c757d; color: white; padding: 2px 6px; border-radius: 6px;",
        }
        style = badge_styles.get(
            obj.status,
            "background-color: #343a40; color: white; padding: 2px 6px; border-radius: 6px;",
        )
        return format_html(
            '<span style="{}">{}</span>', style, obj.get_status_display()
        )

    status_colored.short_description = "Status"

    def verification_status_colored(self, obj):
        badge_styles = {
            UserVerificationStatus.UNVERIFIED: "background-color: #6c757d; color: white; padding: 2px 6px; border-radius: 6px;",
            UserVerificationStatus.EMAIL_VERIFIED: "background-color: #1762b8; color: white; padding: 2px 6px; border-radius: 6px;",
            UserVerificationStatus.PHONE_VERIFIED: "background-color: #ffc107; color: black; padding: 2px 6px; border-radius: 6px;",
            UserVerificationStatus.VERIFIED: "background-color: #28a745; color: white; padding: 2px 6px; border-radius: 6px;",
        }
        style = badge_styles.get(
            obj.verification_status,
            "background-color: #343a40; color: white; padding: 2px 6px; border-radius: 6px;",
        )
        return format_html(
            '<span style="{}">{}</span>', style, obj.get_verification_status_display()
        )

    verification_status_colored.short_description = "Verification Status"

    def important_dates(self, obj):
        # convert datetime to localtime
        last_login = timezone.localtime(obj.last_login) if obj.last_login else None
        created_at = timezone.localtime(obj.created_at) if obj.created_at else None
        updated_at = timezone.localtime(obj.updated_at) if obj.updated_at else None

        # helper function to create a badge for a date
        def date_badge(label, value, color):
            return format_html(
                '<span style="display:inline-block; background-color:{}; color:white; padding:4px 6px; border-radius:4px; font-size:11px; text-align:center; line-height:1.2; margin-right:4px;">'
                "<strong>{}</strong><br>{}</span>",
                color,
                label,
                date_format(value, "SHORT_DATETIME_FORMAT") if value else "—",
            )

        return format_html(
            "{} {} {}",
            date_badge("Last login", last_login, "#1762b8"),
            date_badge("Created", created_at, "#28a745"),
            date_badge("Updated", updated_at, "#6c757d"),
        )

    important_dates.short_description = "Dates"
