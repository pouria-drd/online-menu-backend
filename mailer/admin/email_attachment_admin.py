from django.contrib import admin
from django.utils.html import format_html
from ..models import EmailAttachmentModel


@admin.register(EmailAttachmentModel)
class EmailAttachmentAdmin(admin.ModelAdmin):
    list_display = (
        "short_filename",
        "email_log",
        "content_type",
        "size_display",
        "created_at",
        "download_link",
    )
    list_filter = ("content_type", "created_at")
    search_fields = ("filename", "content_type", "email_log__recipient")
    readonly_fields = (
        "filename",
        "content_type",
        "size",
        "created_at",
        "file_preview",
        "download_link",
    )
    ordering = ("-created_at",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email_log",
                    "file",
                    "filename",
                    "content_type",
                    "size",
                    "file_preview",
                    "download_link",
                    "created_at",
                )
            },
        ),
    )

    def short_filename(self, obj):
        if not obj.filename:
            return "-"
        if len(obj.filename) > 20:
            return f"{obj.filename[:6]}...{obj.filename[-12:]}"
        return obj.filename

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

    def file_preview(self, obj):
        if not obj.file:
            return "-"
        return format_html(
            '<a href="{}" target="_blank">Open Attachment</a>', obj.file.url
        )

    file_preview.short_description = "Preview"

    def download_link(self, obj):
        if not obj.file:
            return "-"
        return format_html(
            '<a class="button" href="{}" download>Download</a>', obj.file.url
        )

    download_link.short_description = "Download"
    download_link.allow_tags = True
