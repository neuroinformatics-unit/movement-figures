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
uv pip install --python .venv -r requirements.txt   # manim 0.22.1, movement 0.17.0
.venv/bin/python fetch_assets.py   # logos from the NIU Dropbox (MOVEMENT_RESOURCES)

cd scenes
../.venv/bin/manim -qm --media_dir ../media s01_formats.py Formats   # 720p draft
../.venv/bin/manim -qm --media_dir ../media s02_analysis.py Analysis
../.venv/bin/manim -qm --media_dir ../media s03_quantify.py Quantify
../.venv/bin/manim -qh --fps 30 ...  # final 1080p30 (the -qh preset is 60 fps)

cd ..
ffmpeg -f concat -safe 0 -i media/concat.txt -c copy media/combined_720p.mp4
```

Segments are rendered separately and joined with ffmpeg's concat demuxer
(`media/concat.txt` lists the three segment files); each segment starts on
the exact frame the previous one ends on.

Not committed (see `.gitignore`):

- `assets/`: logos copied by `fetch_assets.py` (some third-party); only the
  Font Awesome `file-solid-full.svg` is tracked.
- `sleap_data/`: SLEAP-tracked bees and flies clips (`.slp` + `.mp4`), not
  public sample data; needed for segment 3. The flies are unused so far.
- `cache/`: data derived on first render (cleaned tracks, video frames,
  matplotlib plot frames at the render's pixel size); delete to rebuild.
- `media/`, `previews/` (ad-hoc frame grabs for review).

## Code layout (`scenes/`)

- `common.py`: brand constants, header badge, captions, tool chips, the
  isometric data cube and its labels, the shared dataset arrow, and the
  dataset positions used for the hand-overs between segments.
- `mouse.py`: DBTravelator skeletons and video frames (segment 1).
- `analysis_data.py` + `vis_plots.py`: cleaned SLEAP EPM data and the
  trajectory/occupancy frames (segment 2). `octagon_motion()` (two-mice
  octagon speed/distance) is left over and currently unused.
- `bees.py` + `bee_plots.py`: bee tracks, video frames, metrics and the
  staged figure (segment 3).
- `s01_formats.py`, `s02_analysis.py`, `s03_quantify.py`: the scenes.

## Decisions so far

- Concept: "many tools in, one dataset out", then what you can do with it.
  Built with manim from real tracking data.
- Format: 1920×1080, 30 fps, white background, Barlow typeface, Set2 colours
  (`#66c2a5`, `#8da0cb`, `#fc8d62`). Persistent header: URL centred in teal
  (regular weight), logo top right; the URL is on screen, unchanged, for
  the whole video.
- Glanceable for passers-by: big, short captions; one thing to look at at a
  time; restrained animation (things appear rather than fly in); the end
  fades to the header alone so the loop restarts cleanly.
- Formats: shown as tool rows (logo + name, no boxes) for DeepLabCut, SLEAP,
  LightningPose and NWB, plus "and more…" with a generic file icon. Only
  tools the loaders support today; no "coming soon", no code on screen.
- Mouse-first, then a different species. Datasets: DLC DBTravelator 2D
  (segment 1), SLEAP single-mouse EPM (segment 2), SLEAP two bees
  (segment 3).
- The data cube is a true isometric copy of the docs' `data_icon.png`.
- Any real plot must be made with movement's (or xarray's) own plotting
  functions in matplotlib, default look (only font size enlarged, axes off,
  brand colours where colour is a free choice), so it is truthful to what
  users get.
- Saving/export (NWB, netCDF) dropped for now in favour of analysis
  (`netcdf_icon.png` is still fetched but unused).
- Segments 1–2 were kept under 45 s combined.
- End card should credit SWC / NIU and the contributor community, plus the
  Font Awesome icon (CC BY 4.0).

## Status (2026-10-28): segments 1–3, ~60 s combined at 720p

Segment 1, `scenes/s01_formats.py` (~25 s):

1. Title card: header URL and big logo on frame 1; tagline "Python tools
   for analysing animal motion" fades in; the logo alone flies into the
   header's right corner.
2. Real DBTravelator video (247 fps, ~18× slower) alone for ~2 s, then its
   skeleton fades in, the video fades out, the bare skeleton walks on:
   "Do you track animals with / DeepLabCut, SLEAP or similar tools?"
3. Tool rows appear on the left while three skeleton mice (one track
   replayed with different gait phases) run right and stop: "Bring tracks
   from all your favourite / tools and file formats".
4. The cube and dimension labels appear beside them: "…into one tidy
   dataset". Tools and mice fade, leaving the cube.

Segment 2, `scenes/s02_analysis.py` (~16 s):

1. Cube shrinks left; a "clean" arrow (shared with segment 3):
   "Drop outliers, smooth and interpolate tracks".
2. `plot_centroid_trajectory` reveal on cleaned SLEAP EPM: "Visualise
   trajectories"; then the `plot_occupancy` subplot appears and the caption
   completes in place: "… and occupancy heatmaps".
3. Everything but the header, cube and arrow fades.

Segment 3, `scenes/s03_quantify.py` (~19 s):

1. The arrow is relabelled "compute"; the bee clip (49–57 s of
   `sleap_data/bees…`, 1.5× speed, green/orange skeletons) plays as a
   thumbnail below the cube. Caption for the whole segment (wording still
   open): "Quantify motion any way you like".
2. Figure builds up panel by panel: speed, inter-bee distance, head-direction
   polar histograms (antenna bases as left/right pair, 30° bins), all from
   movement + xarray plotting. Fades to the header alone.

Plots and logo bitmaps are rendered/resampled to their exact on-screen pixel
size (`screen_pixels`, `image`) to avoid aliasing; final renders need
`-qh --fps 30`. No 1080p render has been made of the current version yet.

## Next

- Settle the segment 3 caption wording.
- Use the space freed by the header: enlarge content between header and
  caption.
- Optional seamless loop: corner logo grows back to centre at the very end.
- napari ROI clip (Niko's screen recording).
- End card: SWC / NIU credit, contributor count, URL, QR code, Font Awesome
  credit.
- Remove `octagon_motion()` and the netCDF icon if they stay unused.
- Final 1080p30 render of all segments.

## Notes

- movement's `savgol_filter` needs `mode="nearest"` with SciPy >= 1.17 when
  edge windows contain NaNs (worth an upstream issue).
