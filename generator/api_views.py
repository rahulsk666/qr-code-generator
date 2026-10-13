
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from rest_framework.decorators import (
    api_view,
    permission_classes,
    parser_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status

from .models import QRCode
from .serializers import QRCodeSerializer
from .services import build_payload, generate_qr


@api_view(["POST"])
@permission_classes([AllowAny])
@parser_classes([JSONParser])
def generate_qr_api(request):
    try:
        data = request.data

        qr_type = data.get("qr_type", "text")
        content = build_payload(qr_type, data)

        foreground = data.get("foreground_color", "#000000")
        background = data.get("background_color", "#FFFFFF")
        box_size = int(data.get("box_size", 10))
        output_format = data.get("output_format", "png")

        image_bytes = generate_qr(
            content=content,
            foreground=foreground,
            background=background,
            box_size=box_size,
            output_format=output_format,
        )

        record = QRCode.objects.create(
            title=data.get("title", "")[:100],
            qr_type=qr_type,
            content=content,
            foreground_color=foreground,
            background_color=background,
            box_size=box_size,
            output_format=output_format,
        )

        if output_format == "svg":
            content_type = "image/svg+xml"
            extension = "svg"
        else:
            content_type = "image/png"
            extension = "png"

        response = HttpResponse(
            image_bytes,
            content_type=content_type,
        )
        response["Content-Disposition"] = (
            f'attachment; filename="qr-{record.pk}.{extension}"'
        )
        return response

    except (ValidationError, ValueError, TypeError) as exc:
        return Response(
            {"error": str(exc)},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def qr_history_api(request):
    records = QRCode.objects.all()[:100]
    serializer = QRCodeSerializer(records, many=True)
    return Response(serializer.data)
