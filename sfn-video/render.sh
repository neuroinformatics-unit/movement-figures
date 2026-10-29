#!/usr/bin/env bash
# Render every segment and join them into media/movement_SfN_2026_<res>.mp4.
# Usage: ./render.sh [720p|1080p]   (720p draft by default)
set -euo pipefail
cd "$(dirname "$0")"

res=${1:-720p}
case "$res" in
  720p) flags=(-qm) dir=720p30 ;;
  1080p) flags=(-qh --fps 30) dir=1080p30 ;;  # the -qh preset is 60 fps
  *) echo "usage: $0 [720p|1080p]" >&2; exit 1 ;;
esac

segments=(
  "s01_io IO"
  "s02_clean_viz CleanViz"
  "s03_quantify Quantify"
  "s04_gui GUI"
  "s05_community Community"
)
list=media/concat_$res.txt
mkdir -p media
: > "$list"
for segment in "${segments[@]}"; do
  read -r module scene <<< "$segment"
  (cd scenes && ../.venv/bin/manim "${flags[@]}" --media_dir ../media "$module.py" "$scene")
  echo "file '$PWD/media/videos/$module/$dir/$scene.mp4'" >> "$list"
done

# Each segment starts on the frame the previous one ends on, so the joins
# need no re-encoding
ffmpeg -loglevel error -y -f concat -safe 0 -i "$list" -c copy \
  "media/movement_SfN_2026_$res.mp4"
echo "Wrote media/movement_SfN_2026_$res.mp4"
