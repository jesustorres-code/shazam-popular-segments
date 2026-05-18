from __future__ import annotations

import io
import re
from typing import Any

import pytesseract
from PIL import Image, ImageEnhance, ImageOps

from .timecode import duration_from_range, parse_timecode


SEGMENT_PATTERN = re.compile(
    r"(?P<start>\d{1,2}:\d{2}(?::\d{2})?)\s*[-–—]\s*(?P<end>\d{1,2}:\d{2}(?::\d{2})?)"
)


def parse_segment_text(text: str) -> dict[str, Any] | None:
    normalized = text.replace("O", "0").replace("o", "0")
    match = SEGMENT_PATTERN.search(normalized)
    if not match:
        return None

    start = match.group("start")
    end = match.group("end")
    start_seconds = parse_timecode(start)
    end_seconds = parse_timecode(end)
    if end_seconds <= start_seconds:
        return None
    return {
        "start": start,
        "end": end,
        "startSeconds": start_seconds,
        "endSeconds": end_seconds,
        "durationSeconds": duration_from_range(start, end),
    }


def _top_right_crop(image: Image.Image) -> Image.Image:
    width, height = image.size
    left = int(width * 0.42)
    top = 0
    right = width
    bottom = int(height * 0.45)
    return image.crop((left, top, right, bottom))


def _prepare_for_ocr(image: Image.Image) -> Image.Image:
    grayscale = ImageOps.grayscale(image)
    enlarged = grayscale.resize((grayscale.width * 3, grayscale.height * 3))
    contrasted = ImageEnhance.Contrast(enlarged).enhance(2.4)
    return contrasted.point(lambda pixel: 255 if pixel > 150 else 0)


def read_segment_from_screenshot(image_bytes: bytes) -> dict[str, Any]:
    image = Image.open(io.BytesIO(image_bytes))
    crop = _top_right_crop(image)
    prepared = _prepare_for_ocr(crop)
    text = pytesseract.image_to_string(
        prepared,
        config="--psm 6 -c tessedit_char_whitelist=0123456789:-–— ",
    )
    segment = parse_segment_text(text)
    if segment is None:
        raise ValueError("could not read a Shazam segment from the screenshot")
    return {"text": text.strip(), **segment}
