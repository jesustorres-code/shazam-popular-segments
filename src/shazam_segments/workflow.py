from __future__ import annotations

from pathlib import Path
from typing import Any

from .cases import build_case, load_case, popular_segment, slugify, write_case
from .extract import download_audio, extract_clip
from .metadata import search_deezer, search_itunes


def search_metadata(provider: str, query: str) -> dict[str, Any] | None:
    if provider == "deezer":
        return search_deezer(query)
    if provider == "itunes":
        return search_itunes(query)
    raise ValueError(f"unsupported provider: {provider}")


def create_case(
    query: str,
    provider: str = "deezer",
    cases_dir: str | Path = "data/cases",
    slug: str | None = None,
    segment_start: str | None = None,
    segment_end: str | None = None,
) -> dict[str, Any]:
    metadata = search_metadata(provider, query)
    if metadata is None:
        raise ValueError("no metadata result found")

    case_slug = slug or slugify(f"{metadata.get('artist', '')}-{metadata.get('title', '')}")
    case_path = Path(cases_dir) / case_slug / "metadata.json"
    data = build_case(metadata, query, segment_start=segment_start, segment_end=segment_end)
    write_case(case_path, data)
    return {"case": str(case_path), "metadata": data}


def extract_case(
    case_path: str | Path,
    audio: str | Path | None = None,
    outputs_dir: str | Path = "outputs/clips",
    video_seconds: float = 7,
    download_dir: str | Path = "outputs/downloads",
) -> dict[str, Any]:
    case_file = Path(case_path)
    case = load_case(case_file)
    case_slug = case_file.parent.name

    source_audio = Path(audio) if audio else None
    if source_audio is None:
        preview = case.get("preview")
        if not preview:
            raise ValueError("case does not include preview; provide audio")
        source_audio = download_audio(preview, Path(download_dir) / f"{case_slug}-preview.mp3")

    popular = popular_segment(case)
    video = popular_segment(case, video_seconds=video_seconds)

    output_root = Path(outputs_dir)
    popular_output = output_root / f"{case_slug}-popular-{int(popular.start):02d}-{int(popular.start + popular.duration):02d}.mp3"
    video_output = output_root / f"{case_slug}-video-{int(video.start):02d}-{int(video.start + video.duration):02d}.mp3"

    extract_clip(source_audio, popular.start, popular.duration, popular_output)
    extract_clip(source_audio, video.start, video.duration, video_output)

    return {
        "case": str(case_file),
        "audio": str(source_audio),
        "popularClip": str(popular_output),
        "videoClip": str(video_output),
        "popular": {"startSeconds": popular.start, "durationSeconds": popular.duration},
        "video": {"startSeconds": video.start, "durationSeconds": video.duration},
    }


def list_cases(cases_dir: str | Path = "data/cases") -> list[dict[str, Any]]:
    root = Path(cases_dir)
    if not root.exists():
        return []

    cases: list[dict[str, Any]] = []
    for metadata_path in sorted(root.glob("*/metadata.json")):
        data = load_case(metadata_path)
        cases.append({
            "slug": metadata_path.parent.name,
            "path": str(metadata_path),
            "title": data.get("title"),
            "artist": data.get("artist"),
            "durationSeconds": data.get("durationSeconds"),
            "isrc": data.get("isrc"),
            "popularSegment": data.get("shazamPopularSegment") or data.get("popularSegment"),
        })
    return cases


def list_clips(outputs_dir: str | Path = "outputs/clips") -> list[dict[str, Any]]:
    root = Path(outputs_dir)
    if not root.exists():
        return []

    clips: list[dict[str, Any]] = []
    for clip_path in sorted(root.glob("*.mp3")):
        clips.append({
            "name": clip_path.name,
            "path": str(clip_path),
            "sizeBytes": clip_path.stat().st_size,
        })
    return clips
