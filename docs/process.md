# Process

## Pipeline

1. Input song query:
   `artist + title`, ideally with ISRC when known.
2. Resolve metadata:
   duration, ISRC, artists, service IDs.
3. Resolve Shazam Popular Segment:
   prefer explicit text like `00:00 - 00:05`.
4. Normalize timestamps:
   start seconds, end seconds, optional 7s video window.
5. Extract audio:
   `ffmpeg -ss START -t DURATION -i SOURCE OUT.mp3`.
6. Save outputs and metadata in the project folder.

## Visual Fallback Formula

If Shazam only shows a visual bar:

```
start_seconds = start_x / bar_width * total_duration_seconds
end_seconds = end_x / bar_width * total_duration_seconds
```

For the first case, `holanda`, fallback is not needed because Shazam displays `00:00 - 00:05` explicitly.
