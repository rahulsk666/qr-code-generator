from django.contrib import admin

from .models import QRCode


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "qr_type",
        "output_format",
        "created_at",
    )
    list_display_links = ("id", "title")
    list_editable = ("qr_type", "output_format")
    list_filter = ("qr_type", "output_format", "created_at")
    search_fields = ("title", "content")
