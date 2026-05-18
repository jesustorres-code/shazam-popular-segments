from __future__ import annotations

import shutil
import subprocess
import urllib.request
from pathlib import Path


def require_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is required but was not found in PATH")


def audio_duration(input_audio: str | Path) -> float:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(input_audio),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        details = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"ffprobe failed: {details}")
    try:
        return float(result.stdout.strip())
    except ValueError as exc:
        raise RuntimeError("ffprobe did not return a valid audio duration") from exc


def extract_clip(input_audio: str | Path, start: float, duration: float, output_audio: str | Path) -> None:
    if duration <= 0:
        raise ValueError("duration must be positive")

    require_ffmpeg()
    input_duration = audio_duration(input_audio)
    requested_end = start + duration
    if start >= input_duration or requested_end > input_duration + 0.25:
        raise ValueError(
            "requested segment is outside the available audio preview "
            f"({start:.2f}s-{requested_end:.2f}s requested, source is {input_duration:.2f}s). "
            "Use a full audio source or choose a segment inside the downloaded preview."
        )

    output = Path(output_audio)
    output.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "ffmpeg",
        "-y",
        "-ss",
        f"{start:.3f}",
        "-t",
        f"{duration:.3f}",
        "-i",
        str(input_audio),
        "-vn",
        "-c:a",
        "libmp3lame",
        "-q:a",
        "2",
        str(output),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        if output.exists():
            output.unlink()
        details = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"ffmpeg failed: {details}")

    try:
        output_duration = audio_duration(output)
    except RuntimeError as exc:
        if output.exists():
            output.unlink()
        raise RuntimeError(f"generated clip is not valid audio: {exc}") from exc
    if output_duration <= 0:
        if output.exists():
            output.unlink()
        raise RuntimeError("generated clip is empty")


def download_audio(url: str, output_audio: str | Path) -> Path:
    output = Path(output_audio)
    output.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "shazam-popular-segments/0.1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        output.write_bytes(response.read())
    return output
