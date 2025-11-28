from django.contrib import admin
from django.utils.html import format_html

from apps.authentication.models import OTPModel
from apps.authentication.selectors import OTPSelectors
from apps.authentication.repositories import OTPRepository


@admin.register(OTPModel)
class OTPAdmin(admin.ModelAdmin):
    """Admin panel for OTP management using service/repository/selector layers."""

    list_display = (
        "email",
        "otp_type",
        "is_used",
        "attempts",
        "remaining_attempts_display",
        "status_display",
        "expire_at",
        "created_at",
    )

    search_fields = ("email",)
    list_filter = ("otp_type", "is_used", "created_at")

    readonly_fields = (
        "id",
        "email",
        "otp_type",
        "salt",
        "code_hash",
        "is_used",
        "attempts",
        "created_at",
        "updated_at",
        "status_display",
        "remaining_attempts_display",
    )

    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 25

    fieldsets = (
        (
            "OTP Information",
            {
                "fields": (
                    "email",
                    "otp_type",
                    "is_used",
                    "attempts",
                    "remaining_attempts_display",
                    "status_display",
                ),
            },
        ),
        (
            "Security Details",
            {
                "fields": ("salt", "code_hash"),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    # -----------------------------------------
    # Custom display fields (using selectors)
    # -----------------------------------------

    def status_display(self, obj):
        """Display OTP status with colors (using selectors)."""

        if obj.is_used:
            return format_html('<span style="color:#888;">Used</span>')

        if OTPSelectors.is_expired(obj):
            return format_html('<span style="color:#e74c3c;">Expired</span>')

        return format_html('<span style="color:#27ae60;">Active</span>')

    status_display.short_description = "Status"

    def remaining_attempts_display(self, obj):
        """Read from model property (clean access)."""
        return OTPSelectors.remaining_attempts(obj)

    remaining_attempts_display.short_description = "Attempts Left"

    def expire_at(self, obj):
        """Read from model property (clean access)."""
        return OTPSelectors.expire_at(obj)

    expire_at.short_description = "Expire At"

    # -----------------------------------------
    # Admin Actions (using Service / Repo)
    # -----------------------------------------

    actions = ["action_mark_used", "action_delete_expired"]

    @admin.action(description="Mark selected OTPs as used")
    def action_mark_used(self, request, queryset):
        count = 0
        for otp in queryset:
            OTPRepository.mark_used(otp)
            count += 1
        self.message_user(request, f"{count} OTPs marked as used ✓")

    @admin.action(description="Delete expired OTPs")
    def action_delete_expired(self, request, queryset):
        expired_qs = [otp for otp in queryset if OTPSelectors.is_expired(otp)]
        count = len(expired_qs)

        for otp in expired_qs:
            otp.delete()

        self.message_user(request, f"{count} expired OTPs deleted 🧹")

    # -----------------------------------------
    # Permissions
    # -----------------------------------------

    def has_add_permission(self, request):
        return False  # Prevent manual addition
