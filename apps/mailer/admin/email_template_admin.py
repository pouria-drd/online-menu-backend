from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from apps.mailer.models import EmailTemplateModel


@admin.register(EmailTemplateModel)
class EmailTemplateAdmin(admin.ModelAdmin):
    """Admin interface for EmailTemplate."""

    list_display = [
        "name",
        "slug",
        "template_type",
        "is_active",
        "created_at",
        "preview_button",
    ]
    list_filter = ["template_type", "is_active", "created_at"]
    search_fields = ["name", "slug", "subject"]
    readonly_fields = ["created_at", "updated_at"]
    prepopulated_fields = {"slug": ("name",)}

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("name", "slug", "template_type", "is_active")},
        ),
        (
            "Content",
            {"fields": ("subject", "html_content", "text_content", "variables")},
        ),
        (
            "Metadata",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def preview_button(self, obj):
        """Button to preview the template."""
        url = reverse("admin:email_service_emailtemplate_change", args=[obj.pk])
        return format_html('<a class="button" href="{}">Preview</a>', url)

    preview_button.short_description = "Actions"
