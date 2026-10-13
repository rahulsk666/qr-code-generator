
import base64
import math
import xml.etree.ElementTree as ET
from io import BytesIO

import qrcode
from qrcode.image.svg import (
    SvgPathImage,
    SvgImage,
)
from django.core.exceptions import ValidationError
from PIL import Image


SVG_NAMESPACE = "http://www.w3.org/2000/svg"
XLINK_NAMESPACE = "http://www.w3.org/1999/xlink"


def _embed_logo_in_svg(svg_bytes, logo):
    svg = ET.fromstring(svg_bytes)
    view_box = svg.get("viewBox")
    if view_box:
        min_x, min_y, width, height = map(float, view_box.replace(",", " ").split())
    else:
        width = float(svg.get("width", "0").removesuffix("px"))
        height = float(svg.get("height", "0").removesuffix("px"))
        min_x = min_y = 0

    if width <= 0 or height <= 0:
        raise ValidationError("Could not determine SVG QR code dimensions.")

    max_size = max(1, math.floor(min(width, height) / 5))
    logo_image = Image.open(logo).convert("RGBA")
    logo_image.thumbnail((max_size, max_size))
    logo_buffer = BytesIO()
    logo_image.save(logo_buffer, format="PNG")
    logo_data = base64.b64encode(logo_buffer.getvalue()).decode("ascii")

    x = min_x + (width - logo_image.width) / 2
    y = min_y + (height - logo_image.height) / 2
    ET.register_namespace("", SVG_NAMESPACE)
    ET.register_namespace("xlink", XLINK_NAMESPACE)
    ET.SubElement(
        svg,
        f"{{{SVG_NAMESPACE}}}image",
        {
            "x": str(x),
            "y": str(y),
            "width": str(logo_image.width),
            "height": str(logo_image.height),
            "href": f"data:image/png;base64,{logo_data}",
            f"{{{XLINK_NAMESPACE}}}href": f"data:image/png;base64,{logo_data}",
        },
    )
    return ET.tostring(svg, encoding="utf-8", xml_declaration=True)


def build_payload(qr_type, data):
    if qr_type == "text":
        value = data.get("content", "").strip()

    elif qr_type == "wifi":
        ssid = data.get("ssid", "").strip()
        password = data.get("password", "")
        security = data.get("security", "WPA")

        if security not in {"WPA", "WEP", "nopass"}:
            raise ValidationError("Invalid Wi-Fi security type.")

        def escape_wifi(value):
            for char in ("\\", ";", ",", ":", '"'):
                value = value.replace(char, "\\" + char)
            return value

        value = (
            f"WIFI:T:{security};"
            f"S:{escape_wifi(ssid)};"
            f"P:{escape_wifi(password)};;"
        )

    elif qr_type == "email":
        address = data.get("address", "").strip()
        subject = data.get("subject", "")
        body = data.get("body", "")

        from urllib.parse import urlencode

        query = urlencode({"subject": subject, "body": body})
        value = f"mailto:{address}?{query}"

    elif qr_type == "phone":
        phone = data.get("phone", "").strip()
        value = f"tel:{phone}"

    elif qr_type == "vcard":
        name = data.get("name", "").strip()
        phone = data.get("phone", "").strip()
        email = data.get("email", "").strip()
        value = (
            "BEGIN:VCARD\r\n"
            "VERSION:3.0\r\n"
            f"FN:{name}\r\n"
            f"TEL:{phone}\r\n"
            f"EMAIL:{email}\r\n"
            "END:VCARD"
        )

    else:
        raise ValidationError("Unsupported QR type.")

    if not value or len(value) > 2000:
        raise ValidationError(
            "QR content must contain 1–2000 characters."
        )

    return value


def generate_qr(
    content,
    foreground="#000000",
    background="#FFFFFF",
    box_size=10,
    output_format="png",
    logo=None,
):
    if not (
        isinstance(foreground, str)
        and len(foreground) == 7
        and foreground.startswith("#")
        and isinstance(background, str)
        and len(background) == 7
        and background.startswith("#")
    ):
        raise ValidationError("Use colors in #RRGGBB format.")

    try:
        for color in (foreground, background):
            int(color[1:], 16)
    except ValueError:
        raise ValidationError("Invalid hexadecimal color.")

    if not 1 <= box_size <= 20:
        raise ValidationError("Box size must be between 1 and 20.")

    if output_format not in {"png", "svg"}:
        raise ValidationError("Format must be PNG or SVG.")

    factory = {
        "png": None,
        "svg": SvgPathImage,
    }[output_format]

    qr = qrcode.QRCode(
        version=None,
        error_correction=(
            qrcode.constants.ERROR_CORRECT_H
            if logo
            else qrcode.constants.ERROR_CORRECT_M
        ),
        box_size=box_size,
        border=4,
    )
    qr.add_data(content)
    qr.make(fit=True)

    image = qr.make_image(
        image_factory=factory,
        fill_color=foreground,
        back_color=background,
    )

    if logo:
        if output_format == "png":
            image = qr.make_image(
                fill_color=foreground,
                back_color=background,
            ).convert("RGB")

            logo_image = Image.open(logo).convert("RGBA")
            max_logo_size = image.width // 5
            logo_image.thumbnail((max_logo_size, max_logo_size))

            x = (image.width - logo_image.width) // 2
            y = (image.height - logo_image.height) // 2
            image.paste(logo_image, (x, y), logo_image)

    buffer = BytesIO()
    if output_format == "png":
        image.save(buffer, format="PNG")
    else:
        image.save(buffer)

    image_bytes = buffer.getvalue()
    if output_format == "svg" and logo:
        logo.seek(0)
        return _embed_logo_in_svg(image_bytes, logo)
    return image_bytes
