# Deployment

This project is intentionally simple. It does not require a long-running service yet.

## Server Setup

Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install -y git ffmpeg python3 python3-pip
git clone https://github.com/jesustorres-code/shazam-popular-segments.git
cd shazam-popular-segments
python3 -m pip install --user .
```

For development without installing, run commands with `PYTHONPATH=src`:

```bash
PYTHONPATH=src python3 -m shazam_segments.cli --help
```

Verify:

```bash
shazam-segment --help
```

The command above should print usage.

## Run A Clip Extraction

```bash
mkdir -p outputs/clips
shazam-segment extract --audio /path/to/song.mp3 --start 0 --duration 5 --output outputs/clips/song-popular-00-05.mp3
```

## Operational Model

Current workflow:

1. Resolve song metadata and duration.
2. Obtain Shazam Popular Segments timestamp from screenshot, browser, or future automation.
3. Extract the matching clip with `scripts/extract-clip.sh`.
4. Store generated clips in `outputs/clips/`.

## API Mode

Install API dependencies:

```bash
python3 -m pip install --user '.[api]'
```

Run:

```bash
shazam-segment serve --host 0.0.0.0 --port 8000
```

Check:

```bash
curl http://127.0.0.1:8000/health
```

## Artifact Policy

Do not commit generated clips, third-party audio, or Shazam screenshots by default. Keep the repository public and source-focused.
