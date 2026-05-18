from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any


def _fetch_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "shazam-popular-segments/0.1"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def search_deezer(query: str) -> dict[str, Any] | None:
    encoded = urllib.parse.quote(query)
    data = _fetch_json(f"https://api.deezer.com/search?q={encoded}&limit=1")
    results = data.get("data") or []
    if not results:
        return None
    track = results[0]
    return {
        "provider": "deezer",
        "title": track.get("title"),
        "artist": (track.get("artist") or {}).get("name"),
        "deezerId": track.get("id"),
        "isrc": track.get("isrc"),
        "durationSeconds": track.get("duration"),
        "preview": track.get("preview"),
    }


def search_itunes(query: str) -> dict[str, Any] | None:
    encoded = urllib.parse.quote(query)
    data = _fetch_json(f"https://itunes.apple.com/search?term={encoded}&media=music&entity=song&limit=1")
    results = data.get("results") or []
    if not results:
        return None
    track = results[0]
    millis = track.get("trackTimeMillis")
    return {
        "provider": "itunes",
        "title": track.get("trackName"),
        "artist": track.get("artistName"),
        "trackId": track.get("trackId"),
        "durationSeconds": round(millis / 1000) if isinstance(millis, int) else None,
        "preview": track.get("previewUrl"),
        "url": track.get("trackViewUrl"),
    }


def lookup_itunes_track(track_id: int) -> dict[str, Any] | None:
    data = _fetch_json(f"https://itunes.apple.com/lookup?id={track_id}&entity=song")
    results = data.get("results") or []
    if not results:
        return None
    track = results[0]
    millis = track.get("trackTimeMillis")
    return {
        "provider": "itunes",
        "title": track.get("trackName"),
        "artist": track.get("artistName"),
        "trackId": track.get("trackId"),
        "durationSeconds": round(millis / 1000) if isinstance(millis, int) else None,
        "preview": track.get("previewUrl"),
        "url": track.get("trackViewUrl"),
    }
