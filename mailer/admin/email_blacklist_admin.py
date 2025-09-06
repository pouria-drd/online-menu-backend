from django.contrib import admin
from ..models import EmailBlacklistModel


@admin.register(EmailBlacklistModel)
class EmailBlacklistAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "user",
        "is_active",
        "created_by",
        "created_at",
        "updated_at",
    )
    search_fields = ("email", "user__username", "created_by__username")
    list_filter = ("is_active", "created_at")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
