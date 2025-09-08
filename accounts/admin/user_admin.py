from django.contrib import admin
from django.db.models import Prefetch
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.constants import UserStatus
from .user_profile_admin import UserProfileInline
from .user_settings_admin import UserSettingsInline
from accounts.models import UserModel, UserEmailModel, UserPhoneModel


@admin.action(description="Soft-delete selected users")
def soft_delete_users(modeladmin, request, queryset):
    for user in queryset:
        user.soft_delete()


@admin.register(UserModel)
class UserAdmin(BaseUserAdmin):
    """FULLY OPTIMIZED admin configuration for UserModel"""

    inlines = [
        UserProfileInline,
        UserSettingsInline,
    ]

    list_per_page = 25
    list_max_show_all = 100

    # All the previous optimization code here...
    list_display = [
        "username",
        "get_primary_email",
        "get_primary_phone",
        "user_role_info",
        "status_formatted",
        "email_phone_verified",
        "last_login",
        "updated_at",
        "created_at",
    ]

    search_fields = [
        "username",
        "emails__email",
        "phones__phone_number",
    ]

    list_filter = [
        "role",
        "status",
        "is_superuser",
        "groups",
        "emails__is_verified",
        "phones__is_verified",
    ]

    ordering = ["-created_at"]
    readonly_fields = [
        "id",
        "last_login",
        "created_at",
        "updated_at",
        "deleted_at",
        "is_staff",
        "is_active",
        "is_deleted",
        "is_superuser",
        "get_primary_email",
        "get_primary_phone",
        "get_email_verified",
        "get_phone_verified",
    ]
    actions = [soft_delete_users]

    def get_queryset(self, request):
        """Fully optimized queryset"""
        queryset = super().get_queryset(request)
        return queryset.select_related("profile", "settings").prefetch_related(
            Prefetch(
                "emails",
                queryset=UserEmailModel.objects.filter(is_primary=True).only(
                    "id", "user_id", "email", "is_verified", "is_primary"
                ),
                to_attr="primary_emails_cached",
            ),
            Prefetch(
                "phones",
                queryset=UserPhoneModel.objects.filter(is_primary=True).only(
                    "id", "user_id", "phone_number", "is_verified", "is_primary"
                ),
                to_attr="primary_phones_cached",
            ),
            "groups",
            "user_permissions__content_type",
        )

    # Include all the custom methods from the previous code
    def get_primary_email(self, obj):
        if hasattr(obj, "primary_emails_cached"):
            return (
                obj.primary_emails_cached[0].email
                if obj.primary_emails_cached
                else "No email"
            )
        email_obj = obj.emails.filter(is_primary=True).first()
        return email_obj.email if email_obj else "No email"

    get_primary_email.short_description = "Primary Email"
    get_primary_email.admin_order_field = "emails__email"

    def get_primary_phone(self, obj):
        if hasattr(obj, "primary_phones_cached"):
            return (
                obj.primary_phones_cached[0].phone_number
                if obj.primary_phones_cached
                else "No phone"
            )
        phone_obj = obj.phones.filter(is_primary=True).first()
        return phone_obj.phone_number if phone_obj else "No phone"

    get_primary_phone.short_description = "Primary Phone"
    get_primary_phone.admin_order_field = "phones__phone_number"

    def get_email_verified(self, obj):
        if hasattr(obj, "primary_emails_cached"):
            return (
                obj.primary_emails_cached[0].is_verified
                if obj.primary_emails_cached
                else False
            )
        email_obj = obj.emails.filter(is_primary=True).first()
        return email_obj.is_verified if email_obj else False

    get_email_verified.short_description = "Email Verified"
    get_email_verified.boolean = True

    def get_phone_verified(self, obj):
        if hasattr(obj, "primary_phones_cached"):
            return (
                obj.primary_phones_cached[0].is_verified
                if obj.primary_phones_cached
                else False
            )
        phone_obj = obj.phones.filter(is_primary=True).first()
        return phone_obj.is_verified if phone_obj else False

    get_phone_verified.short_description = "Phone Verified"
    get_phone_verified.boolean = True

    def email_phone_verified(self, obj):
        email_verified = self.get_email_verified(obj)
        phone_verified = self.get_phone_verified(obj)

        if email_verified and phone_verified:
            return format_html(
                '<span style="background-color: #127429; color: white; padding: 2px 6px; border-radius: 6px;">Yes (Both)</span>'
            )
        elif email_verified:
            return format_html(
                '<span style="background-color: #1762b8; color: white; padding: 2px 6px; border-radius: 6px;">Yes (Email)</span>'
            )
        elif phone_verified:
            return format_html(
                '<span style="background-color: #1762b8; color: white; padding: 2px 6px; border-radius: 6px;">Yes (Phone)</span>'
            )

        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 2px 6px; border-radius: 6px;">No</span>'
        )

    email_phone_verified.short_description = "Email / Phone Verified"

    # Include all other display methods...
    def user_role_info(self, obj):
        role_colors = {"admin": "#127429", "user": "#1762b8", "menu_owner": "#fd7e14"}
        role_color = role_colors.get(obj.role, "#6c757d")
        role_badge = format_html(
            '<span style="background-color:{}; color:white; padding:2px 6px; border-radius:4px; font-size:11px;">{}</span>',
            role_color,
            obj.role,
        )
        super_text = "Superuser" if obj.is_superuser else "Not Superuser"
        super_color = "#127429" if obj.is_superuser else "#6c757d"
        super_badge = format_html(
            '<span style="background-color:{}; color:white; padding:2px 6px; border-radius:4px; font-size:11px;">{}</span>',
            super_color,
            super_text,
        )
        return format_html("{} {}", role_badge, super_badge)

    user_role_info.short_description = "Role"

    def status_formatted(self, obj):
        badge_styles = {
            UserStatus.ACTIVE: "background-color: #127429; color: white; padding: 2px 6px; border-radius: 6px;",
            UserStatus.INACTIVE: "background-color: #6c757d; color: white; padding: 2px 6px; border-radius: 6px;",
            UserStatus.BANNED: "background-color: #dc3545; color: white; padding: 2px 6px; border-radius: 6px;",
            UserStatus.DELETED: "background-color: #fd7e14; color: white; padding: 2px 6px; border-radius: 6px;",
        }
        style = badge_styles.get(
            obj.status,
            "background-color: #343a40; color: white; padding: 2px 6px; border-radius: 6px;",
        )
        return format_html(
            '<span style="{}">{}</span>', style, obj.get_status_display()
        )

    status_formatted.short_description = "Status"

    # Fieldsets
    fieldsets = (
        (
            "Basic Info",
            {
                "fields": (
                    "id",
                    "username",
                    "get_primary_email",
                    "get_primary_phone",
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
                    "is_staff",
                    "is_active",
                    "is_deleted",
                    "get_email_verified",
                    "get_phone_verified",
                )
            },
        ),
        (
            "Important Dates",
            {"fields": ("last_login", "created_at", "updated_at", "deleted_at")},
        ),
        (
            "Permissions",
            {"classes": ("collapse",), "fields": ("groups", "user_permissions")},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "role", "status"),
            },
        ),
    )
