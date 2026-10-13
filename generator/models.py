
from django.db import models


class QRCode(models.Model):
    TYPE_CHOICES = [
        ("text", "Text / URL"),
        ("wifi", "Wi-Fi"),
        ("email", "Email"),
        ("phone", "Phone"),
        ("vcard", "Contact card"),
    ]

    FORMAT_CHOICES = [
        ("png", "PNG"),
        ("svg", "SVG"),
    ]

    title = models.CharField(max_length=100, blank=True)
    qr_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default="text",
    )
    content = models.TextField(max_length=2000)

    foreground_color = models.CharField(
        max_length=7,
        default="#000000",
    )
    background_color = models.CharField(
        max_length=7,
        default="#FFFFFF",
    )
    box_size = models.PositiveSmallIntegerField(default=10)
    output_format = models.CharField(
        max_length=3,
        choices=FORMAT_CHOICES,
        default="png",
    )

    logo = models.ImageField(
        upload_to="qr_logos/",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title or f"QR Code #{self.pk}"
