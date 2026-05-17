from __future__ import annotations

import shutil
import subprocess
import urllib.request
from pathlib import Path


def require_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is required but was not found in PATH")


def extract_clip(input_audio: str | Path, start: float, duration: float, output_audio: str | Path) -> None:
    if duration <= 0:
        raise ValueError("duration must be positive")

    require_ffmpeg()
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
        details = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"ffmpeg failed: {details}")


def download_audio(url: str, output_audio: str | Path) -> Path:
    output = Path(output_audio)
    output.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "shazam-popular-segments/0.1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        output.write_bytes(response.read())
    return output
