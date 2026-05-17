# Deployment

This project is intentionally simple. It does not require a long-running service yet.

## Server Setup

Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install -y git ffmpeg
git clone https://github.com/jesustorres-code/shazam-popular-segments.git
cd shazam-popular-segments
```

Verify:

```bash
scripts/extract-clip.sh --help
```

The command above should print usage and exit with a non-zero status because no arguments were supplied. That is expected.

## Run A Clip Extraction

```bash
mkdir -p outputs/clips
scripts/extract-clip.sh /path/to/song.mp3 0 5 outputs/clips/song-popular-00-05.mp3
```

## Operational Model

Current workflow:

1. Resolve song metadata and duration.
2. Obtain Shazam Popular Segments timestamp from screenshot, browser, or future automation.
3. Extract the matching clip with `scripts/extract-clip.sh`.
4. Store generated clips in `outputs/clips/`.

## Artifact Policy

Do not commit generated clips, third-party audio, or Shazam screenshots by default. Keep the repository public and source-focused.
