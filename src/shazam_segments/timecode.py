from __future__ import annotations


def parse_timecode(value: str | int | float) -> float:
    """Parse seconds, MM:SS, or HH:MM:SS into seconds."""
    if isinstance(value, (int, float)):
        if value < 0:
            raise ValueError("timecode cannot be negative")
        return float(value)

    text = str(value).strip()
    if not text:
        raise ValueError("timecode is empty")

    if ":" not in text:
        seconds = float(text)
        if seconds < 0:
            raise ValueError("timecode cannot be negative")
        return seconds

    parts = text.split(":")
    if len(parts) not in (2, 3):
        raise ValueError(f"invalid timecode: {value!r}")

    try:
        numbers = [float(part) for part in parts]
    except ValueError as exc:
        raise ValueError(f"invalid timecode: {value!r}") from exc

    if any(part < 0 for part in numbers):
        raise ValueError("timecode cannot be negative")

    if len(numbers) == 2:
        minutes, seconds = numbers
        return minutes * 60 + seconds

    hours, minutes, seconds = numbers
    return hours * 3600 + minutes * 60 + seconds


def format_seconds(seconds: float) -> str:
    total = int(round(seconds))
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def duration_from_range(start: str | int | float, end: str | int | float) -> float:
    start_seconds = parse_timecode(start)
    end_seconds = parse_timecode(end)
    duration = end_seconds - start_seconds
    if duration <= 0:
        raise ValueError("end time must be greater than start time")
    return duration
