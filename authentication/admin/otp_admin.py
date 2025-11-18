from datetime import timedelta
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from authentication.models import OTPModel
from authentication.constants import OTP_EXPIRY_MINUTES


@admin.register(OTPModel)
class OTPAdmin(admin.ModelAdmin):
    """Admin panel for OTP management and debugging."""

    list_display = (
        "channel",
        "target_display",
        "otp_type",
        "created_at",
        "is_used",
        "expired_status",
        "attempts",
        "remaining_attempts_display",
    )

    search_fields = ("email", "phone_number")
    list_filter = ("channel", "otp_type", "is_used", "created_at")

    readonly_fields = (
        "id",
        "channel",
        "email",
        "phone_number",
        "otp_type",
        "salt",
        "code_hash",
        "is_used",
        "attempts",
        "created_at",
        "updated_at",
        "expired_status",
        "expires_at",
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
                    "channel",
                    "email",
                    "phone_number",
                    "otp_type",
                    "is_used",
                    "attempts",
                    "remaining_attempts_display",
                    "expired_status",
                ),
            },
        ),
        (
            "Security Details",
            {
                "fields": (
                    "salt",
                    "code_hash",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "expires_at",
                ),
            },
        ),
    )

    # -------------------------
    # Computed / display fields
    # -------------------------

    def target_display(self, obj):
        """Display target email or phone neatly."""
        if obj.channel == "email":
            return obj.email or "-"
        elif obj.channel == "phone":
            return obj.phone_number or "-"
        return "-"

    target_display.short_description = "Target"

    def expired_status(self, obj):
        """Return a colored tag for OTP expiration."""
        if obj.is_used:
            return format_html('<span style="color: #999;">Used</span>')
        if obj.expired:
            return format_html('<span style="color: #e74c3c;">Expired</span>')
        return format_html('<span style="color: #27ae60;">Active</span>')

    expired_status.short_description = "Status"
    expired_status.admin_order_field = "created_at"

    def expires_at(self, obj):
        """Show when OTP expires."""
        return obj.created_at + timedelta(minutes=OTP_EXPIRY_MINUTES)

    expires_at.short_description = "Expires at"

    def remaining_attempts_display(self, obj):
        """Show attempts left before lockout."""
        return obj.remaining_attempts

    remaining_attempts_display.short_description = "Remaining Attempts"

    # -------------------------
    # Admin actions
    # -------------------------

    actions = ["mark_all_used", "delete_expired"]

    @admin.action(description="Mark selected OTPs as used")
    def mark_all_used(self, request, queryset):
        count = queryset.update(is_used=True)
        self.message_user(request, f"{count} OTPs marked as used ✅")

    @admin.action(description="Delete expired OTPs")
    def delete_expired(self, request, queryset):
        now = timezone.now()
        expired_qs = queryset.filter(
            created_at__lt=now - timedelta(minutes=OTP_EXPIRY_MINUTES)
        )
        count = expired_qs.count()
        expired_qs.delete()
        self.message_user(request, f"{count} expired OTPs deleted 🧹")

    # -------------------------
    # Permissions
    # -------------------------

    def has_add_permission(self, request):
        """Prevent adding OTPs manually."""
        return False
