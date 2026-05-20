from __future__ import annotations

import subprocess
import tempfile
from typing import Any
from pathlib import Path

from flask import Flask, after_this_request, jsonify, request, send_file

from shazam_segments.metadata import cookie_jar_from_text, youtube_video_id_from_url
from shazam_segments.metadata import resolve_youtube_music_url
from shazam_segments.workflow import resolve_metadata


app = Flask(__name__)


INDEX_HTML = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>YouTube Music Lookup</title>
    <style>
      :root {
        color-scheme: light;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: #f5f6f8;
        color: #17181c;
      }
      body { margin: 0; }
      main { max-width: 960px; margin: 0 auto; padding: 32px 20px 48px; }
      header { display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; margin-bottom: 20px; }
      h1 { margin: 0 0 6px; font-size: 28px; line-height: 1.15; }
      p { margin: 0; color: #626773; }
      section { background: #fff; border: 1px solid #d8dbe2; border-radius: 8px; padding: 16px; margin-bottom: 16px; }
      label { display: block; font-size: 13px; font-weight: 650; margin: 12px 0 6px; }
      input, select, textarea { width: 100%; box-sizing: border-box; border: 1px solid #c8ccd5; border-radius: 6px; padding: 10px; font: inherit; }
      textarea { min-height: 140px; resize: vertical; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12px; }
      button { border: 0; border-radius: 6px; padding: 10px 13px; margin-top: 14px; background: #1167d8; color: #fff; font-weight: 700; cursor: pointer; }
      button.secondary { background: #2f3440; margin-right: 8px; }
      button.success { background: #0f7b45; margin-left: 8px; }
      button:disabled { background: #8b93a1; cursor: wait; }
      pre { min-height: 260px; overflow: auto; background: #111318; color: #eef2ff; border-radius: 6px; padding: 12px; font-size: 12px; line-height: 1.45; }
      .status { border: 1px solid #d8dbe2; border-radius: 6px; padding: 10px 12px; background: #fff; min-width: 130px; text-align: right; font-size: 14px; }
      .hint { margin-top: 6px; font-size: 12px; }
      .credentials { border-left: 4px solid #1167d8; }
      .preview { display: none; gap: 10px; align-items: center; border: 1px solid #e0e3ea; border-radius: 6px; padding: 10px; }
      .preview.active { display: grid; }
      .preview strong { font-size: 13px; overflow-wrap: anywhere; }
      audio { width: 100%; height: 34px; }
      @media (max-width: 700px) {
        header { display: block; }
        .status { margin-top: 14px; text-align: left; }
      }
    </style>
  </head>
  <body>
    <main>
      <header>
        <div>
          <h1>YouTube Music Lookup</h1>
          <p>Resolve YouTube Music links with optional cookies and return structured track data.</p>
        </div>
        <div class="status" id="health">Checking...</div>
      </header>

      <section>
        <label for="url">YouTube Music URL</label>
        <input id="url" placeholder="https://music.youtube.com/watch?v=..." />
        <label for="provider">Preview Provider</label>
        <select id="provider">
          <option value="deezer">Deezer Preview</option>
          <option value="itunes">iTunes Preview</option>
        </select>
      </section>

      <section class="credentials">
        <label for="cookies">Credenciales de YouTube Music / Cookies</label>
        <textarea id="cookies" spellcheck="false" placeholder="Pega aqui tus cookies de YouTube Music en formato cookies.txt o la cabecera Cookie: ..."></textarea>
        <p class="hint">Este es el espacio para tus credenciales. Quedan editables y se guardan solo en este navegador, no en el servidor.</p>
        <button type="button" class="secondary" onclick="clearCookies()">Clear Cookies</button>
        <button id="submit" onclick="resolveTrack()">Resolve Track</button>
        <button id="download" class="success" onclick="downloadTrack()">Download Audio</button>
      </section>

      <section>
        <div class="preview" id="preview">
          <strong id="previewTitle"></strong>
          <audio id="previewAudio" controls preload="none"></audio>
        </div>
        <pre id="result">Waiting for a YouTube Music URL.</pre>
      </section>
    </main>

    <script>
      const COOKIES_KEY = "youtubeMusicCookies";

      function show(value) {
        document.getElementById("result").textContent = typeof value === "string" ? value : JSON.stringify(value, null, 2);
      }

      function loadSavedCookies() {
        const saved = localStorage.getItem(COOKIES_KEY);
        if (saved) document.getElementById("cookies").value = saved;
      }

      function saveCookies() {
        localStorage.setItem(COOKIES_KEY, document.getElementById("cookies").value);
      }

      function clearCookies() {
        localStorage.removeItem(COOKIES_KEY);
        document.getElementById("cookies").value = "";
      }

      function renderPreview(metadata) {
        const preview = document.getElementById("preview");
        const audio = document.getElementById("previewAudio");
        if (!metadata || !metadata.preview) {
          preview.classList.remove("active");
          audio.removeAttribute("src");
          return;
        }
        document.getElementById("previewTitle").textContent = [metadata.artist, metadata.title].filter(Boolean).join(" - ");
        audio.src = metadata.preview;
        preview.classList.add("active");
      }

      async function loadHealth() {
        try {
          const response = await fetch("/health");
          const data = await response.json();
          document.getElementById("health").textContent = data.status;
        } catch (error) {
          document.getElementById("health").textContent = "offline";
        }
      }

      async function resolveTrack() {
        const button = document.getElementById("submit");
        button.disabled = true;
        renderPreview(null);
        show("Resolving...");
        try {
          saveCookies();
          const response = await fetch("/resolve", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              url: document.getElementById("url").value,
              provider: document.getElementById("provider").value,
              cookiesText: document.getElementById("cookies").value || null
            })
          });
          const data = await response.json();
          if (!response.ok) throw new Error(JSON.stringify(data, null, 2));
          renderPreview(data.metadata);
          show(data);
        } catch (error) {
          show(error.message);
        } finally {
          button.disabled = false;
        }
      }

      async function downloadTrack() {
        const button = document.getElementById("download");
        button.disabled = true;
        show("Preparing download...");
        try {
          saveCookies();
          const response = await fetch("/download", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              url: document.getElementById("url").value,
              cookiesText: document.getElementById("cookies").value || null
            })
          });
          if (!response.ok) {
            const data = await response.json();
            throw new Error(JSON.stringify(data, null, 2));
          }
          const blob = await response.blob();
          const disposition = response.headers.get("Content-Disposition") || "";
          const match = disposition.match(/filename="?([^";]+)"?/i);
          const filename = match ? match[1] : "youtube-music-audio.m4a";
          const link = document.createElement("a");
          link.href = URL.createObjectURL(blob);
          link.download = filename;
          document.body.appendChild(link);
          link.click();
          URL.revokeObjectURL(link.href);
          link.remove();
          show({ ok: true, download: filename });
        } catch (error) {
          show(error.message);
        } finally {
          button.disabled = false;
        }
      }

      loadSavedCookies();
      document.getElementById("cookies").addEventListener("input", saveCookies);
      loadHealth();
    </script>
  </body>
</html>
"""


def resolve_track(url: str, provider: str, cookies_text: str | None = None) -> dict[str, Any]:
    youtube = resolve_youtube_music_url(url, cookies_text)
    try:
        resolved_query, metadata = resolve_metadata(provider, youtube["query"])
        metadata_error = None
    except Exception as exc:
        resolved_query = youtube["query"]
        metadata = None
        metadata_error = str(exc)

    return {
        "youtube": youtube,
        "query": resolved_query,
        "metadata": metadata,
        "metadataError": metadata_error,
    }


def write_netscape_cookies(cookies_text: str | None, output_path: Path) -> bool:
    jar = cookie_jar_from_text(cookies_text)
    if jar is None:
        return False

    lines = ["# Netscape HTTP Cookie File"]
    for cookie in jar:
        include_subdomains = "TRUE" if cookie.domain.startswith(".") else "FALSE"
        secure = "TRUE" if cookie.secure else "FALSE"
        expires = str(cookie.expires or 0)
        lines.append("\t".join([cookie.domain, include_subdomains, cookie.path, secure, expires, cookie.name, cookie.value]))
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def download_audio(url: str, cookies_text: str | None = None) -> Path:
    temp_root = Path(tempfile.mkdtemp(prefix="youtube-music-download-"))
    output_template = temp_root / "%(title).160B [%(id)s].%(ext)s"
    video_id = youtube_video_id_from_url(url)
    download_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else url
    command = [
        "python3",
        "-m",
        "yt_dlp",
        "--js-runtimes",
        "node",
        "--remote-components",
        "ejs:github",
        "--extractor-args",
        "youtube:player_client=web,android",
        "--no-playlist",
        "--format",
        "bestaudio/best",
        "--extract-audio",
        "--audio-format",
        "m4a",
        "--audio-quality",
        "0",
        "--output",
        str(output_template),
        download_url,
    ]

    cookies_path = temp_root / "cookies.txt"
    if write_netscape_cookies(cookies_text, cookies_path):
        command[3:3] = ["--cookies", str(cookies_path)]

    completed = subprocess.run(command, check=False, capture_output=True, text=True, timeout=180)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "yt-dlp download failed")

    downloads = sorted(path for path in temp_root.iterdir() if path.is_file() and path.name != "cookies.txt")
    if not downloads:
        raise RuntimeError("download completed but no audio file was produced")
    return downloads[0]


@app.get("/")
def index() -> str:
    return INDEX_HTML


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "youtube-music-lookup"})


@app.post("/resolve")
def resolve():
    payload = request.get_json(silent=True) or {}
    url = str(payload.get("url") or "").strip()
    provider = str(payload.get("provider") or "deezer")
    cookies_text = payload.get("cookiesText")

    if provider not in {"deezer", "itunes"}:
        return jsonify({"ok": False, "error": "provider must be deezer or itunes"}), 400
    if not url:
        return jsonify({"ok": False, "error": "YouTube Music URL is required"}), 400

    try:
        return jsonify(resolve_track(url, provider, cookies_text))
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 502


@app.post("/download")
def download():
    payload = request.get_json(silent=True) or {}
    url = str(payload.get("url") or "").strip()
    cookies_text = payload.get("cookiesText")
    if not url:
        return jsonify({"ok": False, "error": "YouTube Music URL is required"}), 400

    try:
        audio_path = download_audio(url, cookies_text)
    except RuntimeError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 502
    except subprocess.TimeoutExpired:
        return jsonify({"ok": False, "error": "download timed out"}), 504

    @after_this_request
    def cleanup(response):
        try:
            temp_root = audio_path.parent
            for path in temp_root.iterdir():
                path.unlink(missing_ok=True)
            temp_root.rmdir()
        except OSError:
            pass
        return response

    return send_file(audio_path, as_attachment=True, download_name=audio_path.name)


if __name__ == "__main__":
    import os

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "7777")))
