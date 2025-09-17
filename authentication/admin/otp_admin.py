from django.contrib import admin
from authentication.models import OTPModel


@admin.register(OTPModel)
class OTPAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "usecase",
        "attempts",
        "max_attempts",
        "used",
        "is_expired_display",
        "used_at",
        "created_at",
        "expires_at",
        "last_attempted",
    )
    list_filter = ("usecase", "used", "created_at", "expires_at")
    search_fields = ("user__username", "user__email", "user__phone_number")
    ordering = ("-created_at",)
    readonly_fields = (
        "code_hash",
        "created_at",
        "last_attempted",
        "expires_at",
        "used_at",
    )

    def is_expired_display(self, obj):
        return obj.is_expired

    is_expired_display.boolean = True
    is_expired_display.short_description = "Expired"

    actions = ["delete_expired"]

    def delete_expired(self, request, queryset):
        """Delete expired OTP codes."""
        count = queryset.filter(is_expired=True).delete()
        self.message_user(request, f"{count} OTP code(s) deleted.")
