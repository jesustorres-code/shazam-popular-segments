from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .cases import build_case, load_case, popular_segment, slugify, write_case
from .extract import download_audio, extract_clip
from .metadata import search_deezer, search_itunes
from .timecode import duration_from_range, parse_timecode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="shazam-segment")
    subparsers = parser.add_subparsers(dest="command", required=True)

    extract = subparsers.add_parser("extract", help="Extract a clip from timestamps or a case JSON file.")
    extract.add_argument("--audio", required=True, help="Source audio file.")
    extract.add_argument("--output", required=True, help="Output MP3 path.")
    extract.add_argument("--start", help="Start timestamp in seconds, MM:SS, or HH:MM:SS.")
    extract.add_argument("--end", help="End timestamp in seconds, MM:SS, or HH:MM:SS.")
    extract.add_argument("--duration", type=float, help="Clip duration in seconds.")
    extract.add_argument("--case", help="Case JSON file with shazamPopularSegment.")
    extract.add_argument("--video-seconds", type=float, help="Override case segment duration, e.g. 7.")

    metadata = subparsers.add_parser("metadata", help="Search song metadata.")
    metadata.add_argument("query", help="Song query, e.g. 'artist - title'.")
    metadata.add_argument("--provider", choices=["deezer", "itunes"], default="deezer")

    case = subparsers.add_parser("case", help="Create and extract song cases.")
    case_subparsers = case.add_subparsers(dest="case_command", required=True)

    create = case_subparsers.add_parser("create", help="Create a case JSON from metadata search.")
    create.add_argument("query", help="Song query, e.g. 'artist - title'.")
    create.add_argument("--provider", choices=["deezer", "itunes"], default="deezer")
    create.add_argument("--cases-dir", default="data/cases", help="Directory where case folders are created.")
    create.add_argument("--slug", help="Case folder slug. Defaults to title/artist slug.")
    create.add_argument("--segment-start", help="Known Shazam Popular Segment start.")
    create.add_argument("--segment-end", help="Known Shazam Popular Segment end.")

    case_extract = case_subparsers.add_parser("extract", help="Extract popular/video clips from a case JSON.")
    case_extract.add_argument("case", help="Case JSON path.")
    case_extract.add_argument("--audio", help="Source audio file. If omitted, preview URL from case is downloaded.")
    case_extract.add_argument("--outputs-dir", default="outputs/clips", help="Directory for generated clips.")
    case_extract.add_argument("--video-seconds", type=float, default=7, help="Video clip duration from segment start.")
    case_extract.add_argument("--download-dir", default="outputs/downloads", help="Directory for downloaded preview audio.")

    return parser


def run_extract(args: argparse.Namespace) -> int:
    if args.case:
        case = load_case(args.case)
        segment = popular_segment(case, video_seconds=args.video_seconds)
        extract_clip(args.audio, segment.start, segment.duration, args.output)
        print(json.dumps({"output": args.output, "startSeconds": segment.start, "durationSeconds": segment.duration}, indent=2))
        return 0

    if args.start is None:
        raise SystemExit("--start is required when --case is not provided")

    start = parse_timecode(args.start)
    if args.duration is not None:
        duration = args.duration
    elif args.end is not None:
        duration = duration_from_range(args.start, args.end)
    else:
        raise SystemExit("either --duration or --end is required")

    extract_clip(args.audio, start, duration, args.output)
    print(json.dumps({"output": args.output, "startSeconds": start, "durationSeconds": duration}, indent=2))
    return 0


def run_metadata(args: argparse.Namespace) -> int:
    result = search_deezer(args.query) if args.provider == "deezer" else search_itunes(args.query)
    if result is None:
        print("No result found", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


def _search_metadata(provider: str, query: str) -> dict | None:
    return search_deezer(query) if provider == "deezer" else search_itunes(query)


def run_case_create(args: argparse.Namespace) -> int:
    result = _search_metadata(args.provider, args.query)
    if result is None:
        print("No result found", file=sys.stderr)
        return 1

    base_slug = args.slug or slugify(f"{result.get('artist', '')}-{result.get('title', '')}")
    case_path = Path(args.cases_dir) / base_slug / "metadata.json"
    data = build_case(result, args.query, segment_start=args.segment_start, segment_end=args.segment_end)
    write_case(case_path, data)
    print(json.dumps({"case": str(case_path), "metadata": data}, indent=2, ensure_ascii=False))
    return 0


def run_case_extract(args: argparse.Namespace) -> int:
    case_path = Path(args.case)
    case = load_case(case_path)
    slug = case_path.parent.name

    audio = Path(args.audio) if args.audio else None
    if audio is None:
        preview = case.get("preview")
        if not preview:
            raise SystemExit("case does not include preview; provide --audio")
        audio = download_audio(preview, Path(args.download_dir) / f"{slug}-preview.mp3")

    popular = popular_segment(case)
    video = popular_segment(case, video_seconds=args.video_seconds)

    outputs_dir = Path(args.outputs_dir)
    popular_output = outputs_dir / f"{slug}-popular-{int(popular.start):02d}-{int(popular.start + popular.duration):02d}.mp3"
    video_output = outputs_dir / f"{slug}-video-{int(video.start):02d}-{int(video.start + video.duration):02d}.mp3"

    extract_clip(audio, popular.start, popular.duration, popular_output)
    extract_clip(audio, video.start, video.duration, video_output)

    print(json.dumps({
        "case": str(case_path),
        "audio": str(audio),
        "popularClip": str(popular_output),
        "videoClip": str(video_output),
        "popular": {"startSeconds": popular.start, "durationSeconds": popular.duration},
        "video": {"startSeconds": video.start, "durationSeconds": video.duration},
    }, indent=2, ensure_ascii=False))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "extract":
        return run_extract(args)
    if args.command == "metadata":
        return run_metadata(args)
    if args.command == "case":
        if args.case_command == "create":
            return run_case_create(args)
        if args.case_command == "extract":
            return run_case_extract(args)

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
