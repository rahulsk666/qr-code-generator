
import base64
from io import BytesIO

import qrcode
from django.shortcuts import render


def qr(request):
    qr_code = None
    text = ""

    if request.method == "POST":
        text = request.POST.get("text", "").strip()

        if text and len(text) <= 2000:
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )

            qr.add_data(text)
            qr.make(fit=True)

            image = qr.make_image(
                fill_color="black",
                back_color="white",
            )

            buffer = BytesIO()
            image.save(buffer, format="PNG")

            qr_code = base64.b64encode(
                buffer.getvalue()
            ).decode("utf-8")

    return render(
        request,
        "generator/index.html",
        {
            "qr_code": qr_code,
            "text": text,
        },
    )