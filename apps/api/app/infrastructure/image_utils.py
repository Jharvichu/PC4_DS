"""Shared image decoding/validation (RF 2.1: only JPEG/PNG; no SSRF via http fetch)."""

import base64
import binascii
import io

from PIL import Image, UnidentifiedImageError

from app.shared.exceptions import ValidationError

ALLOWED_FORMATS = {"JPEG", "PNG"}


def decode_image_data_url(data_url: str) -> Image.Image:
    """Decode a base64 data URL into a PIL Image.

    Only `data:image/...;base64,...` URLs are accepted -- external http(s) URLs
    are rejected outright to avoid SSRF, since every caller in this app (pets,
    sightings, image search) always sends a base64 data URL from the browser.
    """
    if not data_url.startswith("data:image/"):
        raise ValidationError("Only base64 data URLs (JPEG/PNG) are accepted, not external URLs")

    if "," not in data_url:
        raise ValidationError("Malformed data URL: missing base64 payload")

    _header, _, b64data = data_url.partition(",")
    try:
        raw = base64.b64decode(b64data, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise ValidationError(f"Invalid base64 image data: {exc}")

    try:
        Image.open(io.BytesIO(raw)).verify()  # cheap integrity check; invalidates the file pointer
        image = Image.open(io.BytesIO(raw))  # re-open for actual use
    except UnidentifiedImageError as exc:
        raise ValidationError(f"Could not decode image: {exc}")

    if image.format not in ALLOWED_FORMATS:
        raise ValidationError(f"Unsupported image format: {image.format}. Only JPEG/PNG are allowed")

    return image
