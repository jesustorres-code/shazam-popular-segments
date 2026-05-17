# Shazam Popular Segments

Prototype for finding the most popular Shazam segment of a song and extracting a short audio clip for automated video workflows.

## Goal

Given a song, produce:

- stable song metadata: title, artist, ISRC, duration
- Shazam Popular Segments timestamps
- a short extracted clip, usually 5s from Shazam or 7s for video use

## Workspace Layout

- `docs/` - project notes and design decisions
- `data/cases/` - per-song metadata and extracted structured data
- `inputs/screenshots/` - Shazam screenshots or visual source material
- `outputs/clips/` - generated audio clips ready for review/use
- `scripts/` - prototype scripts
- `notes/` - working notes, logs, experiments

## Install

Requirements:

- Linux server or workstation
- `git`
- `ffmpeg`
- `bash`

Clone:

```bash
git clone https://github.com/jesustorres-code/shazam-popular-segments.git
cd shazam-popular-segments
```

Install system dependency on Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install -y ffmpeg
```

## Usage

Extract a clip from a local audio file:

```bash
scripts/extract-clip.sh input.mp3 0 5 outputs/clips/example-00-05.mp3
```

Arguments:

- `input.mp3` - source audio
- `0` - start time in seconds
- `5` - clip duration in seconds
- `outputs/clips/example-00-05.mp3` - output file

For a Shazam Popular Segment shown as `00:00 - 00:05`, use:

```bash
scripts/extract-clip.sh input.mp3 0 5 outputs/clips/song-popular-00-05.mp3
```

For a 7-second video clip starting at the same point:

```bash
scripts/extract-clip.sh input.mp3 0 7 outputs/clips/song-video-00-07.mp3
```

## Current Case

Song: `holanda`
Artists: `EL DE LA TINTA, Angel Cervantes, Sahir Montoya`
ISRC: `MXUM72503506`
Duration: `03:44` / `224s`
Shazam Popular Segment: `00:00 - 00:05`
Video Clip Candidate: `00:00 - 00:07`

## Current Outputs

- `outputs/clips/holanda-popular-00-05.mp3`
- `outputs/clips/holanda-video-00-07.mp3`

Generated clips and screenshots are kept locally and ignored by Git by default. They may contain third-party copyrighted media or service UI captures. Commit only metadata, docs, and source scripts unless there is a clear reason to version a specific artifact.

## Notes

Shazam blocks direct access from this server with `405 Not allowed`, even through Playwright/Chromium. The current reliable route is:

1. Get metadata from Deezer/iTunes/MusicBrainz or another stable source.
2. Use a Shazam screenshot or browser session from a reachable network.
3. Read `Popular Segments` text directly when available.
4. Fall back to visual timeline mapping only when timestamps are not shown.
5. Extract clips with `ffmpeg`.
