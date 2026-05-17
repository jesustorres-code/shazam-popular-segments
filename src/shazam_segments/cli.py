from __future__ import annotations

import argparse
import json
import sys

from .cases import load_case, popular_segment
from .extract import extract_clip
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


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "extract":
        return run_extract(args)
    if args.command == "metadata":
        return run_metadata(args)

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
