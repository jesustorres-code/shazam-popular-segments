from __future__ import annotations

import json
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
