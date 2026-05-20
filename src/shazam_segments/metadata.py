from __future__ import annotations

import http.cookiejar
import json
import re
import urllib.parse
import urllib.request
from http.cookiejar import Cookie, CookieJar
from typing import Any


USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36"


def _fetch(url: str, cookie_jar: CookieJar | None = None) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar)) if cookie_jar else None
    with (opener.open(request, timeout=20) if opener else urllib.request.urlopen(request, timeout=20)) as response:
        return response.read()


def _fetch_json(url: str, cookie_jar: CookieJar | None = None) -> dict[str, Any]:
    return json.loads(_fetch(url, cookie_jar).decode("utf-8"))


def _fetch_text(url: str, cookie_jar: CookieJar | None = None) -> str:
    return _fetch(url, cookie_jar).decode("utf-8", errors="replace")


def _make_cookie(domain: str, path: str, secure: bool, expires: int | None, name: str, value: str) -> Cookie:
    return Cookie(
        version=0,
        name=name,
        value=value,
        port=None,
        port_specified=False,
        domain=domain,
        domain_specified=domain.startswith("."),
        domain_initial_dot=domain.startswith("."),
        path=path or "/",
        path_specified=True,
        secure=secure,
        expires=expires,
        discard=expires is None,
        comment=None,
        comment_url=None,
        rest={},
        rfc2109=False,
    )


def cookie_jar_from_text(cookies_text: str | None) -> CookieJar | None:
    text = (cookies_text or "").strip()
    if not text:
        return None

    jar = http.cookiejar.CookieJar()
    if text.startswith("[") or text.startswith("{"):
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict):
            parsed = parsed.get("cookies")
        if isinstance(parsed, list):
            for item in parsed:
                if not isinstance(item, dict):
                    continue
                name = str(item.get("name") or "")
                value = str(item.get("value") or "")
                domain = str(item.get("domain") or ".youtube.com")
                path = str(item.get("path") or "/")
                expires = item.get("expirationDate")
                expires_int = int(expires) if isinstance(expires, (float, int)) and expires > 0 else None
                if name:
                    jar.set_cookie(_make_cookie(domain, path, bool(item.get("secure", True)), expires_int, name, value))
            return jar

    if "\n" not in text and (";" in text or "=" in text) and "\t" not in text:
        header = re.sub(r"^Cookie:\s*", "", text, flags=re.IGNORECASE)
        for part in header.split(";"):
            if "=" not in part:
                continue
            name, value = part.strip().split("=", 1)
            if name:
                jar.set_cookie(_make_cookie(".youtube.com", "/", True, None, name, value))
                jar.set_cookie(_make_cookie(".google.com", "/", True, None, name, value))
        return jar

    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 7:
            continue
        domain, _include_subdomains, path, secure, expires, name, value = parts
        try:
            expires_int = int(expires) if expires and int(expires) > 0 else None
        except ValueError:
            expires_int = None
        jar.set_cookie(_make_cookie(domain, path, secure.upper() == "TRUE", expires_int, name, value))
    return jar


def _extract_balanced_json(text: str, marker: str) -> dict[str, Any] | None:
    marker_index = text.find(marker)
    if marker_index < 0:
        return None
    start = text.find("{", marker_index)
    if start < 0:
        return None

    depth = 0
    in_string = False
    escape = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start : index + 1])
    return None


def _youtube_music_page_data(url: str, cookies_text: str | None = None) -> dict[str, Any] | None:
    cookie_jar = cookie_jar_from_text(cookies_text)
    page = _fetch_text(url, cookie_jar)
    player = _extract_balanced_json(page, "ytInitialPlayerResponse")
    if not player:
        return None

    details = player.get("videoDetails") or {}
    microformat = (player.get("microformat") or {}).get("playerMicroformatRenderer") or {}
    title = details.get("title") or microformat.get("title", {}).get("simpleText")
    author = details.get("author") or microformat.get("ownerChannelName")
    length_seconds = details.get("lengthSeconds")
    return {
        "url": url,
        "videoId": details.get("videoId") or youtube_video_id_from_url(url),
        "title": title,
        "author": author,
        "durationSeconds": int(length_seconds) if str(length_seconds or "").isdigit() else None,
        "query": compose_youtube_music_query(title, author),
        "source": "youtube-page",
    }


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
        r"\s*[\[(](?:(?:(?:official|oficial)\s+)?(?:music\s+)?(?:video|audio|lyric video|visualizer)|(?:video|audio)\s+(?:official|oficial))[\])]",
        "",
        clean_title,
        flags=re.IGNORECASE,
    ).strip()
    clean_author = re.sub(r"\s+-\s+Topic$", "", author or "", flags=re.IGNORECASE).strip()
    if clean_author:
        clean_title = re.sub(
            rf"^{re.escape(clean_author)}\s+(?:[-–—]|x|×|feat\.?|ft\.?)\s+",
            "",
            clean_title,
            flags=re.IGNORECASE,
        ).strip()
    return " ".join(part for part in (clean_author, clean_title) if part).strip()


def youtube_video_id_from_url(url: str) -> str | None:
    parsed = urllib.parse.urlparse(url)
    if parsed.hostname == "youtu.be":
        return parsed.path.strip("/") or None
    query = urllib.parse.parse_qs(parsed.query)
    video_ids = query.get("v")
    return video_ids[0] if video_ids else None


def resolve_youtube_music_url(url: str, cookies_text: str | None = None) -> dict[str, Any]:
    if not url.strip():
        raise ValueError("YouTube Music URL is required")

    if cookies_text and (page_data := _youtube_music_page_data(url, cookies_text)):
        if page_data.get("query"):
            return page_data

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
        "source": "oembed",
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
