
from rest_framework import serializers
from .models import QRCode


class QRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCode
        fields = [
            "id",
            "title",
            "qr_type",
            "content",
            "foreground_color",
            "background_color",
            "box_size",
            "output_format",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
