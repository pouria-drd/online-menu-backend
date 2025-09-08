from django.contrib import admin
from accounts.models import UserPhoneModel


@admin.register(UserPhoneModel)
class UserPhoneAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "phone_number",
        "is_primary",
        "is_verified",
        "created_at",
        "updated_at",
        "verified_at",
    ]

    search_fields = ["user__username", "phone_number"]

    readonly_fields = ["is_verified", "verified_at"]

    list_filter = ["is_primary", "is_verified", "created_at", "updated_at"]

    list_select_related = ["user"]  # Optimize foreign key display

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")

    actions = ["mark_as_verified", "mark_as_unverified"]

    def mark_as_verified(self, request, queryset):
        for phone in queryset:
            phone.mark_as_verified()
        self.message_user(request, "Phone numbers marked as verified.")

    mark_as_verified.short_description = "Mark selected phone numbers as verified"

    def mark_as_unverified(self, request, queryset):
        for phone in queryset:
            phone.mark_as_unverified()
        self.message_user(request, "Phone numbers marked as unverified.")

    mark_as_unverified.short_description = "Mark selected phone numbers as unverified"
