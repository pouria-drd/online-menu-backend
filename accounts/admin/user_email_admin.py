from django.contrib import admin
from accounts.models import UserEmailModel


@admin.register(UserEmailModel)
class UserEmailAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "email",
        "is_primary",
        "is_verified",
        "created_at",
        "updated_at",
        "verified_at",
    ]

    search_fields = ["user__username", "email"]

    readonly_fields = ["is_verified", "verified_at"]

    list_filter = ["is_primary", "is_verified", "created_at", "updated_at"]

    list_select_related = ["user"]  # Optimize foreign key display

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")

    actions = ["mark_as_verified", "mark_as_unverified"]

    def mark_as_verified(self, request, queryset):
        for email in queryset:
            email.mark_as_verified()
        self.message_user(request, "Emails marked as verified.")

    mark_as_verified.short_description = "Mark selected emails as verified"

    def mark_as_unverified(self, request, queryset):
        for email in queryset:
            email.mark_as_unverified()
        self.message_user(request, "Emails marked as unverified.")

    mark_as_unverified.short_description = "Mark selected emails as unverified"
