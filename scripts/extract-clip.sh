#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 4 ]]; then
  echo "Usage: $0 INPUT_AUDIO START_SECONDS DURATION_SECONDS OUTPUT_AUDIO" >&2
  exit 2
fi

input="$1"
start="$2"
duration="$3"
output="$4"

mkdir -p "$(dirname "$output")"

ffmpeg -y \
  -ss "$start" \
  -t "$duration" \
  -i "$input" \
  -vn \
  -c:a libmp3lame \
  -q:a 2 \
  "$output"
