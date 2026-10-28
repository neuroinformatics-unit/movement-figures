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
../.venv/bin/manim -qm --media_dir ../media s01_formats.py Formats   # 720p draft
../.venv/bin/manim -qm --media_dir ../media s02_analysis.py Analysis
../.venv/bin/manim -qh ...                                           # 1080p30
```

Segments are rendered separately and joined with ffmpeg's concat demuxer;
segment 2 starts on the exact frame segment 1 ends on. Data derived from
movement's sample datasets (cleaned tracks, video frames, matplotlib plot
frames) is cached in `cache/` on first render; delete it to rebuild.

## Decisions so far

- Concept: "many tools in, one dataset out", then what you can do with it.
  Built with manim from movement's real sample data.
- Format: 1920×1080, 30 fps, white background, Barlow typeface, Set2 colours
  (`#66c2a5`, `#8da0cb`, `#fc8d62`). Persistent corner badge (logo + URL).
  Combined length limit: 45 s for the segments so far.
- Glanceable for passers-by: big, short captions; one thing to look at at a
  time; restrained animation (things appear rather than fly in); the end
  fades to the badge so the loop restarts cleanly.
- Formats: only those the loaders support today (DeepLabCut, SLEAP,
  LightningPose, Anipose, COCO, VIA-tracks, NWB), as compact file cards.
  No third-party logos, no "coming soon", no code on screen.
- Mouse-first, a little species variety later. Datasets: SLEAP EPM,
  DLC DBTravelator 2D, SLEAP two-mice octagon.
- The data cube is a true isometric copy of the docs' `data_icon.png`.
- Any real plot must be made with movement's (or xarray's) own plotting
  functions in matplotlib, default look (only font size enlarged, axes off),
  so it is truthful to what users get.
- Saving/export (NWB, netCDF) dropped for now in favour of analysis.
- End card should credit SWC / NIU and the contributor community.

## Status (2026-10-28): segments 1 and 2, ~44 s combined

Segment 1, `scenes/s01_formats.py` (~26 s):

1. Title card → logo shrinks into the corner badge.
2. Real DBTravelator video (247 fps, played ~18× slower) alone for ~2 s, then
   its skeleton fades in on the mouse, the video fades out and the bare
   skeleton walks on: "Do you track animals in videos with / DeepLabCut,
   SLEAP or similar tools?" (cleaned as in movement's `scale` example,
   23 of 43 keypoints; far-side limbs at 40% opacity).
3. Format cards appear; three skeleton mice (green / purple / orange, the
   same track replayed with different gait phases) run right and stop:
   "Bring tracks from your favourite tool or format…"
4. The cube and its labels appear beside them: "…into one tidy dataset".
   Cards and mice fade, leaving the cube for the handover.

Segment 2, `scenes/s02_analysis.py` (~18 s):

1. Cube shrinks left (labels vanish instantly); a "clean" arrow appears:
   "Drop outliers, smooth and interpolate tracks".
2. A matplotlib figure from `plot_centroid_trajectory` (60 s of cleaned
   SLEAP EPM, each video frame a real re-plot of a growing time slice):
   "Visualise trajectories".
3. Only then does the `plot_occupancy` subplot appear (whole session):
   "Visualise trajectories and occupancy heatmaps". Holds, fades to badge.
   Both panels sit on the video frame where the trajectory ends (borrowed
   from the DLC EPM sample, which tracks the same recording).

## Next

- Quantification panel (after Visualise): options discussed so far are the
  octagon mice's speed (`compute_speed`) and inter-mouse distance, plotted
  with xarray's `.plot`, or heading (`compute_forward_vector_angle`).
  `analysis_data.octagon_motion()` already computes the first two.
- napari ROI clip (Niko's screen recording).
- End card: SWC / NIU credit, contributor count, URL, QR code.
- Species variety: bees / flies SLEAP data in `sleap_data/` (not committed).

## Notes

- movement's `savgol_filter` needs `mode="nearest"` with SciPy >= 1.17 when
  edge windows contain NaNs (worth an upstream issue).
