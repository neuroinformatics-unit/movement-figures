# SfN 2026 booth video

A silent (~2 min) looping video advertising movement, for the shared NWB/DANDI
booth at SfN, Washington DC, 15–18 Nov 2026. The NWB organisers asked for a
2–5 min video that works without audio; on-screen captions carry the
narration. This is independent of the reproducible figures in the rest of
this repo.

## Setup

```bash
# needs system ffmpeg, plus pango/cairo headers to build manimpango:
#   sudo apt install ffmpeg libpango1.0-dev libcairo2-dev pkg-config
# a uv-managed Python is needed (it ships Python.h)
uv venv --python 3.12 --python-preference only-managed .venv
uv pip install --python .venv -r requirements.txt
.venv/bin/python fetch_assets.py

cd scenes
../.venv/bin/manim -qm --media_dir ../media s01_formats.py Formats  # 720p draft
../.venv/bin/manim -qh --media_dir ../media s01_formats.py Formats  # 1080p30
```

The cleaned DBTravelator track is cached in `cache/` on first render.

## Decisions so far

- Concept: "many tools in, one dataset out" (interoperability as the core
  message), built with manim from real sample data. Brief napari ROI-drawing
  clip later, which Niko will screen-record.
- Format: 1920×1080, 30 fps, white background, Barlow typeface, Set2 colours
  (`#66c2a5`, `#8da0cb`, `#fc8d62`). Persistent corner badge (logo + URL).
- Glanceable for passers-by: big, short captions; each segment should make
  sense on its own; the end should loop back to the start.
- Formats: only those currently supported by the loaders (DeepLabCut, SLEAP,
  LightningPose, Anipose, COCO, VIA-tracks, NWB). No "coming soon".
  Shown as file icons with extensions, no third-party logos.
- No code on screen.
- Mouse-first, with a little species variety to signal species-agnosticism.
  Preferred datasets: SLEAP EPM, DLC DBTravelator 2D, SLEAP two-mice octagon.
- Title card: the movement logo + "Python tools for analysing animal motion".
- Export framed as "open scientific data standards": NWB and netCDF.
- End card should credit SWC / NIU and the contributor community
  (contributor count from the GitHub API at render time).

## Status: prototype of segment 1 (`scenes/s01_formats.py`, ~45 s)

1. Title card → logo shrinks into the corner badge.
2. Format cards slide in: "Bring tracks from your favourite tool or format…"
3. Dots fly from the cards and coalesce into three side-view mouse skeletons
   (green / purple / orange, matching the data-cube slabs):
   "…as keypoints on each animal's body".
4. The mice walk in three travelator lanes: "…tracked frame by frame".
   One real DBTravelator track (frames 195–350, cleaned as in the movement
   `scale` example, 23 of 43 keypoints) replayed with different gait phases
   to fake three individuals. Far-side (left) limbs drawn at 40% opacity.
5. Mice shrink left, the data cube builds on the right with dimension labels:
   "…into one tidy dataset" → "Every animal, every keypoint, every frame" →
   "Same tools for every species, every tracker".
6. Cube → NWB and netCDF: "Save to open scientific data standards".

Paused on 2026-10-28 to collect colleagues' feedback on this prototype.

## Open questions

- Faded real video behind the skeletons for a moment (e.g. middle lane only)?
- Walk speed (currently ~8× slow motion over 4.5 s)?
- Keep or drop the "Same tools for every species, every tracker" caption?
- Add DANDI after NWB? Mention saving back to tracker formats?

## Remaining storyboard

- Clean: noisy → filtered → interpolated tracks.
- Compute: speed / heading overlays on real mice.
- Analyse: ROI drawing in napari (Niko's recording) → occupancy / time in ROI.
- End card: SWC / NIU credit, contributor count, URL, QR code; loops.
