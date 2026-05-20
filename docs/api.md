# API

Stage 4 adds a small HTTP API around the CLI workflow.

Stage 5 starts a lightweight product layer with a built-in dashboard. It does not include authentication yet by design.

## Install

```bash
python3 -m pip install --user '.[api]'
```

## Run

```bash
shazam-segment serve --host 0.0.0.0 --port 8000
```

Local development without installing:

```bash
PYTHONPATH=src python3 -m shazam_segments.cli serve --host 127.0.0.1 --port 8000
```

## Endpoints

### Dashboard

```bash
open http://127.0.0.1:8000/
```

### Health

```bash
curl http://127.0.0.1:8000/health
```

### Metadata

```bash
curl 'http://127.0.0.1:8000/metadata?query=EL%20DE%20LA%20TINTA%20Sahir%20Montoya%20holanda&provider=deezer'
```

### Resolve

Uses the Shazam `/song/<id>/<slug>` ID for Apple/iTunes lookup when available, then resolves provider metadata. If ID lookup is unavailable, it derives a query from the final Shazam URL slug. This does not extract clips and does not invent a Shazam Popular Segment.

```bash
curl -X POST http://127.0.0.1:8000/resolve \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "",
    "provider": "deezer",
    "shazamUrl": "https://www.shazam.com/song/1471572221/smack-that-feat-eminem"
  }'
```

### Segment From Screenshot

Reads the Shazam Popular Segment from the top-right area of a screenshot.

```bash
curl -X POST http://127.0.0.1:8000/segment-from-screenshot \
  -F 'file=@shazam-screenshot.png'
```

### Create Case

```bash
curl -X POST http://127.0.0.1:8000/cases \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "EL DE LA TINTA Sahir Montoya holanda",
    "provider": "deezer",
    "segmentStart": "00:00",
    "segmentEnd": "00:05"
  }'
```

If `query` is empty and `shazamUrl` is present, the API derives a search query from the final Shazam URL slug.

### Extract Case

```bash
curl -X POST http://127.0.0.1:8000/extract \
  -H 'Content-Type: application/json' \
  -d '{
    "casePath": "data/cases/el-de-la-tinta-holanda/metadata.json",
    "videoSeconds": 7
  }'
```

### Run Full Process

Creates the case and extracts both clips in one request. Shazam currently supplies the segment timestamp manually from the UI/screenshot.

```bash
curl -X POST http://127.0.0.1:8000/run \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "EL DE LA TINTA Sahir Montoya holanda",
    "provider": "deezer",
    "shazamUrl": "https://www.shazam.com/track/...",
    "segmentStart": "00:00",
    "segmentEnd": "00:05",
    "videoSeconds": 7
  }'
```

### List Clips

```bash
curl http://127.0.0.1:8000/clips
```

### Download Or Preview Clip

```bash
curl -O http://127.0.0.1:8000/clips/holanda-popular-00-05.mp3
```

### YouTube Music Resolve With Cookies

The dashboard accepts either Netscape `cookies.txt` rows exported from the browser or a raw `Cookie:` header. Cookies are used only in-memory for that request and are not written to case files.

```bash
curl -X POST http://127.0.0.1:8000/youtube-music/resolve \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://music.youtube.com/watch?v=rOC4rMWFnOo",
    "provider": "itunes",
    "cookiesText": "# Netscape HTTP Cookie File\n.youtube.com\tTRUE\t/\tTRUE\t1893456000\tSID\t..."
  }'
```

## Current Limitations

- Jobs are synchronous.
- Generated clips are written to local disk.
- No authentication by design in the current product shell.
- No queue or persistent job database yet.
- Shazam segment lookup is not fully automated yet because Shazam blocks this VPS; paste the timestamp from Shazam for now.
