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
../.venv/bin/manim -qh --fps 30 ...  # final 1080p30 (the -qh preset is 60 fps)
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

## Status (2026-10-28): segments 1–3, ~61 s combined

Segment 1, `scenes/s01_formats.py` (~26 s):

1. Title card → logo shrinks into the corner badge.
2. Real DBTravelator video (247 fps, ~18× slower) alone for ~2 s, then its
   skeleton fades in, the video fades out, the bare skeleton walks on:
   "Do you track animals with / DeepLabCut, SLEAP or similar tools?"
3. Four tool cards (logo + name: DeepLabCut, SLEAP, LightningPose, NWB);
   three skeleton mice run right and stop: "Bring tracks from all your
   favourite / tools and file formats".
4. The cube and labels appear beside them: "…into one tidy dataset".

Segment 2, `scenes/s02_analysis.py` (~16 s):

1. Cube shrinks left; a "clean" arrow (shared with segment 3):
   "Drop outliers, smooth and interpolate tracks".
2. `plot_centroid_trajectory` reveal on cleaned SLEAP EPM: "Visualise
   trajectories"; then the `plot_occupancy` subplot appears and the caption
   completes in place: "… and occupancy heatmaps".
3. Everything but the cube and arrow fades.

Segment 3, `scenes/s03_quantify.py` (~19 s):

1. The arrow is relabelled "compute"; the bee clip (49–57 s of
   `sleap_data/bees…`, 1.5× speed, brand-coloured skeletons) plays as a
   thumbnail below the cube. Caption for the whole segment (wording still
   open): "Quantify motion any way you like".
2. Figure builds up: speed, inter-bee distance, head-direction polar
   histograms (antenna bases as left/right pair, 30° bins), all from
   movement + xarray plotting in brand colours. Fades to badge.

Plots are rendered at their exact on-screen pixel size (`screen_pixels`)
to avoid aliasing; final renders need `-qh --fps 30`.

## Next

- Settle the segment 3 caption wording.
- napari ROI clip (Niko's screen recording).
- End card: SWC / NIU credit, contributor count, URL, QR code.
- `sleap_data/` (bees, flies; not committed) is needed to render segment 3.

## Notes

- movement's `savgol_filter` needs `mode="nearest"` with SciPy >= 1.17 when
  edge windows contain NaNs (worth an upstream issue).
