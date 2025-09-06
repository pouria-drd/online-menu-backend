from django.contrib import admin
from ..models import EmailTemplateModel


@admin.register(EmailTemplateModel)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "template_type",
        "subject",
        "is_active",
        "updated_at",
        "created_at",
    )
    search_fields = ("name", "subject", "template_type")
    list_filter = ("template_type", "is_active")
    readonly_fields = ("updated_at", "created_at")
    ordering = ("-created_at",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "template_type",
                    "subject",
                    "description",
                    "body_text",
                    "body_html",
                    "variables",
                    "is_active",
                    "updated_at",
                    "created_at",
                )
            },
        ),
    )
