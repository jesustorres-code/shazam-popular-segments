# Roadmap

## Current Stage

Stage 1: validated prototype.

The project can already:

- resolve a real song case
- store metadata
- read a Shazam Popular Segment from a screenshot
- extract 5s and 7s clips with `ffmpeg`
- run from a public GitHub repository

## Current Implementation Focus: Stage 2

Turn the prototype into a reproducible command-line tool.

### Goals

- Provide one clear command for clip extraction.
- Keep metadata, inputs, and outputs organized.
- Make installation work on another server.
- Avoid committing generated media or copyrighted artifacts.

### Tasks

1. Create a proper CLI entrypoint. (initial version done)
   Example:
   ```bash
   shazam-segment extract --audio song.mp3 --start 0 --duration 7
   ```

2. Add structured case files.
   Example:
   ```json
   {
     "title": "holanda",
     "artists": ["EL DE LA TINTA", "Angel Cervantes", "Sahir Montoya"],
     "isrc": "MXUM72503506",
     "durationSeconds": 224,
     "popularSegment": {
       "start": "00:00",
       "end": "00:05"
     }
   }
   ```

3. Add metadata lookup helpers. (initial Deezer/iTunes helpers done)
   Initial providers:
   - Deezer
   - iTunes Search API

4. Add screenshot parsing flow.
   First version can accept manually entered timestamps.
   Later version should use OCR/vision.

5. Add tests. (initial timecode/case tests done)
   Cover timestamp parsing, duration math, output naming, and ffmpeg command generation.

6. Improve deployment docs.
   Include Ubuntu setup, clone, install, run, and expected output.

## Stage 3

Semi-automated workflow:

- query song metadata (initial case create done)
- attach screenshot
- read or enter Popular Segment (manual timestamp entry done)
- generate clips (initial case extract done)
- write a report JSON

## Stage 4

Service/API:

- REST API (initial synchronous FastAPI service done)
- job queue
- status endpoint
- clip download endpoint
- Docker deployment

## Stage 5

Product shell:

- web dashboard (initial version done)
- case and clip listing (initial version done)
- create/extract actions from the browser (initial version done)
- direct run tab for song query + Shazam timestamp (initial version done)
- optional Shazam URL field stored with each case (initial version done)
- authentication intentionally skipped for now
- later: history, batch workflow, better reports, and download endpoints

## Immediate Recommendation

Build Stage 2 first:

1. CLI
2. structured JSON cases
3. metadata lookup
4. cleaner clip extraction
5. tests
