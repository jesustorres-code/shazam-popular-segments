# Flask YouTube Music Web App

This path matches the browser-to-service flow for the YouTube Music project:

```text
Browser
  -> HTTPS through Cloudflare Tunnel
  -> VM port 7777
  -> Flask app.py
  -> YouTube Music URL and optional cookies
  -> YouTube/oEmbed or authenticated YouTube page fetch
  -> Deezer/iTunes preview metadata when available
  -> yt-dlp audio download when requested
  -> JSON response in the browser
```

## Install

```bash
python3 -m pip install --user '.[flask]'
```

## Run

```bash
PYTHONPATH=src PORT=7777 python3 app.py
```

Open:

```text
http://127.0.0.1:7777/
```

For Cloudflare Tunnel, route public HTTPS traffic to:

```text
http://127.0.0.1:7777
```

For a temporary quick tunnel without a named Cloudflare tunnel:

```bash
tools/cloudflared tunnel --url http://127.0.0.1:7777 --no-autoupdate
```

## Resolve API

```bash
curl -X POST http://127.0.0.1:7777/resolve \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://music.youtube.com/watch?v=rOC4rMWFnOo",
    "provider": "deezer",
    "cookiesText": null
  }'
```

`cookiesText` accepts either Netscape `cookies.txt` rows or a raw `Cookie:` header. Cookies are used only in-memory for the request and are not saved.

## Download API

```bash
curl -X POST http://127.0.0.1:7777/download \
  -H 'Content-Type: application/json' \
  -o song.m4a \
  -d '{
    "url": "https://music.youtube.com/watch?v=rOC4rMWFnOo",
    "cookiesText": null
  }'
```

When cookies are supplied, Flask writes them to a temporary Netscape cookie file for `yt-dlp`, then deletes the temporary directory after sending the audio file.

The download path normalizes `music.youtube.com` URLs to `www.youtube.com/watch?v=...`, enables Node for JavaScript challenge solving, allows the `yt-dlp-ejs` remote component, and avoids the `web_music` client that requires a GVS PO Token.
