from __future__ import annotations

import json
import re
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


def compose_youtube_music_query(title: str | None, author: str | None) -> str:
    clean_title = re.sub(r"\s+", " ", title or "").strip()
    clean_title = re.sub(
        r"\s*[\[(](official\s+)?(music\s+)?(video|audio|lyric video|visualizer)[\])]",
        "",
        clean_title,
        flags=re.IGNORECASE,
    ).strip()
    clean_author = re.sub(r"\s+-\s+Topic$", "", author or "", flags=re.IGNORECASE).strip()
    if clean_author:
        clean_title = re.sub(
            rf"^{re.escape(clean_author)}\s+[-–—]\s+",
            "",
            clean_title,
            flags=re.IGNORECASE,
        ).strip()
    return " ".join(part for part in (clean_author, clean_title) if part).strip()


def resolve_youtube_music_url(url: str) -> dict[str, Any]:
    if not url.strip():
        raise ValueError("YouTube Music URL is required")

    encoded = urllib.parse.quote(url, safe="")
    data = _fetch_json(f"https://www.youtube.com/oembed?format=json&url={encoded}")
    title = data.get("title")
    author = data.get("author_name")
    query = compose_youtube_music_query(title, author)
    if not query:
        raise ValueError("could not derive a song query from the YouTube Music URL")
    return {
        "url": url,
        "title": title,
        "author": author,
        "query": query,
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
