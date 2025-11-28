from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from apps.mailer.models import EmailLogModel


@admin.register(EmailLogModel)
class EmailLogAdmin(admin.ModelAdmin):
    """Admin interface for EmailLog."""

    list_display = [
        "recipient_email",
        "subject",
        "status",
        "template_link",
        "sent_at",
        "created_at",
    ]
    list_filter = ["status", "created_at", "sent_at"]
    search_fields = ["recipient_email", "recipient_name", "subject"]
    readonly_fields = [
        "template",
        "recipient_email",
        "recipient_name",
        "subject",
        "context_data",
        "error_message",
        "sent_at",
        "opened_at",
        "clicked_at",
        "created_at",
        "updated_at",
    ]

    fieldsets = (
        ("Recipient Information", {"fields": ("recipient_email", "recipient_name")}),
        (
            "Email Details",
            {"fields": ("template", "subject", "status", "context_data")},
        ),
        ("Tracking", {"fields": ("sent_at", "opened_at", "clicked_at")}),
        (
            "Error Information",
            {"fields": ("error_message",), "classes": ("collapse",)},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def has_add_permission(self, request):
        """Disable manual log creation."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow deletion for cleanup."""
        return True

    def template_link(self, obj):
        """Link to the associated template."""
        if obj.template:
            url = reverse(
                "admin:email_service_emailtemplate_change", args=[obj.template.pk]
            )
            return format_html('<a href="{}">{}</a>', url, obj.template.name)
        return "-"

    template_link.short_description = "Template"
