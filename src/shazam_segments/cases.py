from __future__ import annotations

import json
import re
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .timecode import duration_from_range, parse_timecode


@dataclass(frozen=True)
class Segment:
    start: float
    duration: float


def load_case(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_case(path: str | Path, data: dict[str, Any]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug or "song"


def query_from_shazam_url(url: str | None) -> str | None:
    if not url:
        return None

    parsed = urllib.parse.urlparse(url)
    parts = [part for part in parsed.path.split("/") if part]
    if not parts:
        return None

    slug = parts[-1]
    if slug.isdigit() and len(parts) >= 2:
        slug = parts[-2]

    query = re.sub(r"[-_]+", " ", slug).strip()
    return query or None


def build_case(
    metadata: dict[str, Any],
    query: str,
    segment_start: str | None = None,
    segment_end: str | None = None,
    shazam_url: str | None = None,
) -> dict[str, Any]:
    case: dict[str, Any] = {
        "query": query,
        "title": metadata.get("title"),
        "artist": metadata.get("artist"),
        "provider": metadata.get("provider"),
        "durationSeconds": metadata.get("durationSeconds"),
        "preview": metadata.get("preview"),
    }
    for key in ("isrc", "deezerId", "trackId", "url"):
        if metadata.get(key) is not None:
            case[key] = metadata[key]

    if shazam_url:
        case["shazamUrl"] = shazam_url

    if segment_start and segment_end:
        start_seconds = parse_timecode(segment_start)
        end_seconds = parse_timecode(segment_end)
        if end_seconds <= start_seconds:
            raise ValueError("segment end must be greater than start")
        case["shazamPopularSegment"] = {
            "start": segment_start,
            "end": segment_end,
            "startSeconds": start_seconds,
            "endSeconds": end_seconds,
        }

    return case


def popular_segment(case: dict[str, Any], video_seconds: float | None = None) -> Segment:
    segment = case.get("shazamPopularSegment") or case.get("popularSegment")
    if not isinstance(segment, dict):
        raise ValueError("case file does not include shazamPopularSegment")

    start = parse_timecode(segment.get("startSeconds", segment.get("start")))
    if video_seconds is not None:
        if video_seconds <= 0:
            raise ValueError("video seconds must be positive")
        return Segment(start=start, duration=float(video_seconds))

    if "endSeconds" in segment:
        end = parse_timecode(segment["endSeconds"])
        duration = end - start
        if duration <= 0:
            raise ValueError("segment end must be greater than start")
        return Segment(start=start, duration=duration)

    if "end" not in segment:
        raise ValueError("segment requires end/endSeconds or --video-seconds")

    return Segment(start=start, duration=duration_from_range(segment["start"], segment["end"]))
