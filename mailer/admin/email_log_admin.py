from django.contrib import admin
from django.utils.html import format_html
from ..models import EmailLogModel, EmailAttachmentModel


class EmailAttachmentInline(admin.TabularInline):
    model = EmailAttachmentModel
    extra = 0
    readonly_fields = (
        "short_filename",
        "content_type",
        "size_display",
        "download_link",
        "created_at",
    )
    fields = (
        "short_filename",
        "content_type",
        "size_display",
        "download_link",
        "created_at",
    )

    def short_filename(self, obj):
        if not obj.filename:
            return "-"
        return (
            f"{obj.filename[:6]}...{obj.filename[-12:]}"
            if len(obj.filename) > 20
            else obj.filename
        )

    short_filename.short_description = "Filename"

    def size_display(self, obj):
        if obj.size is None:
            return "-"
        if obj.size < 1024:
            return f"{obj.size} B"
        elif obj.size < 1024 * 1024:
            return f"{obj.size / 1024:.1f} KB"
        return f"{obj.size / (1024 * 1024):.2f} MB"

    size_display.short_description = "Size"

    def download_link(self, obj):
        if not obj.file:
            return "-"
        return format_html(
            '<a class="button" href="{}" download>Download</a>', obj.file.url
        )

    download_link.short_description = "Download"


@admin.register(EmailLogModel)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = (
        "recipient",
        "subject",
        "status",
        "priority",
        "attempts",
        "user",
        "sent_at",
        "created_at",
    )
    search_fields = ("recipient", "subject", "user__username")
    list_filter = ("status", "priority", "created_at", "sent_at")
    readonly_fields = ("created_at", "updated_at", "sent_at")
    ordering = ("-created_at",)
    inlines = [EmailAttachmentInline]
