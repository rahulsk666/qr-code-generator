import base64

from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify
from django.shortcuts import render

from .models import QRCode
from .services import build_payload, generate_qr


def qr(request):
    context = {
        "qr_type": "text",
        "text": "",
        "box_size": 10,
        "foreground_color": "#000000",
        "background_color": "#ffffff",
        "output_format": "png",
        "security": "WPA",
        "qr_history": QRCode.objects.all()[:100],
    }

    if request.method == "POST":
        form_data = request.POST.copy()
        form_data["content"] = form_data.get("text", "")
        logo = request.FILES.get("logo")

        context.update({
            "title": request.POST.get("title", ""),
            "qr_type": request.POST.get("qr_type", "text"),
            "text": request.POST.get("text", ""),
            "ssid": request.POST.get("ssid", ""),
            "password": request.POST.get("password", ""),
            "security": request.POST.get("security", "WPA"),
            "address": request.POST.get("address", ""),
            "subject": request.POST.get("subject", ""),
            "body": request.POST.get("body", ""),
            "phone": request.POST.get("phone", ""),
            "name": request.POST.get("name", ""),
            "email": request.POST.get("email", ""),
            "foreground_color": request.POST.get(
                "foreground_color", "#000000"
            ),
            "background_color": request.POST.get(
                "background_color", "#ffffff"
            ),
            "box_size": request.POST.get("box_size", "10"),
            "output_format": request.POST.get("output_format", "png"),
        })

        try:
            content = build_payload(context["qr_type"], form_data)
            box_size = int(context["box_size"])
            output_format = context["output_format"]
            image_bytes = generate_qr(
                content=content,
                foreground=context["foreground_color"],
                background=context["background_color"],
                box_size=box_size,
                output_format=output_format,
                logo=logo,
            )

            title = context["title"][:100]
            record = QRCode.objects.create(
                title=title,
                qr_type=context["qr_type"],
                content=content,
                foreground_color=context["foreground_color"],
                background_color=context["background_color"],
                box_size=box_size,
                output_format=output_format,
            )

            if output_format == "svg":
                content_type = "image/svg+xml"
                extension = "svg"
            else:
                content_type = "image/png"
                extension = "png"

            safe_title = slugify(record.title) or "code"
            context.update({
                "qr_code": (
                    f"data:{content_type};base64,"
                    f"{base64.b64encode(image_bytes).decode('ascii')}"
                ),
                "download_filename": f"qr-{safe_title}.{extension}",
                "qr_history": QRCode.objects.all()[:100],
            })
        except (ValidationError, ValueError, TypeError, OSError) as exc:
            if isinstance(exc, ValidationError):
                message = "; ".join(exc.messages)
            else:
                message = str(exc)
            context["error"] = message

    return render(request, "generator/index.html", context)
