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
../.venv/bin/manim -qm --media_dir ../media s01_io.py IO   # 720p draft
../.venv/bin/manim -qm --media_dir ../media s02_clean_viz.py CleanViz
../.venv/bin/manim -qm --media_dir ../media s03_quantify.py Quantify
../.venv/bin/manim -qm --media_dir ../media s04_gui.py GUI
../.venv/bin/manim -qm --media_dir ../media s05_community.py Community
../.venv/bin/manim -qh --fps 30 ...  # final 1080p30 (the -qh preset is 60 fps)

cd ..
ffmpeg -f concat -safe 0 -i media/concat.txt -c copy media/combined_720p.mp4
```

Segments are rendered separately and joined with ffmpeg's concat demuxer
(`media/concat.txt` lists the five segment files); each segment starts on
the exact frame the previous one ends on.

Not committed (see `.gitignore`):

- `assets/`: logos copied by `fetch_assets.py` (some third-party; the Python
  SVG is rasterised with Inkscape) and Niko's napari screen recording
  `movement_napari_bees_workflow_2026-10-29.mp4` (35.7 s, 1080p30), needed
  for segment 4. Copied by hand (not in the Dropbox resources): the
  recording, `NIU_logo_transparent.png` and `UCL-logo-white-simple.png`
  (`qr-code.svg` is no longer used). Only the
  icons are tracked: Font Awesome `file-solid-full.svg` and
  `github-brands.svg` (CC BY 4.0, credited in segment 5) and GitHub's
  Octicons `octicon-law-24.svg` (MIT, also credited in segment 5).
- `sleap_data/`: SLEAP-tracked bees and flies clips (`.slp` + `.mp4`), not
  public sample data; needed for segment 3. The flies are unused so far.
- `cache/`: data derived on first render, and `contributors.txt` (the
  People page's contributor names, fetched once; delete to refresh), (cleaned tracks, video frames,
  matplotlib plot frames at the render's pixel size); delete to rebuild.
- `media/`, `previews/` (ad-hoc frame grabs for review).

## Code layout (`scenes/`)

- `common.py`: brand constants, header badge, captions, small-print credits, tool chips, the
  isometric data cube and its labels, the shared dataset arrow, and the
  dataset positions used for the hand-overs between segments.
- `mouse.py`: DBTravelator skeletons and video frames (segment 1).
- `clean_viz_data.py` + `clean_viz_plots.py`: cleaned DLC EPM data, the
  raw/cleaned trace layers, trajectory/occupancy figures and the video clip
  (segment 2).
- `bees.py` + `bee_plots.py`: bee tracks, video frames, metrics and the
  staged figure (segment 3).
- `community.py`: contributor names from movement's People page.
- `s01_io.py`, `s02_clean_viz.py`, `s03_quantify.py`, `s04_gui.py`,
  `s05_community.py`: the scenes (classes `IO`, `CleanViz`, `Quantify`,
  `GUI`, `Community`).

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
  (segment 1), DLC single-mouse EPM (segment 2), SLEAP two bees
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
- Every video shown carries a small-print data credit below it while it is
  large (Holly Morley; Loukia Katsouri; Pereira et al., Nature Methods,
  2022).

## Status (2026-10-29): segments 1–5, ~109 s combined at 720p

Segment 1 (io), `scenes/s01_io.py` (~23 s):

1. Title card: header URL and big logo on frame 1; tagline "Python tools
   for analysing animal motion" fades in; the logo alone flies into the
   header's right corner.
2. Real DBTravelator video (247 fps, ~18× slower) alone for ~2 s, credited
   "Data: Holly Morley" below it; then its skeleton fades in over the video
   for ~2 s, the video fades out, the bare skeleton walks on briefly:
   "Do you track animals with / DeepLabCut, SLEAP or similar tools?"
3. Tool rows appear on the left while three skeleton mice (one track
   replayed with different gait phases) run right and stop: "Bring tracks
   from all your favourite / tools and file formats".
4. The cube and dimension labels appear beside them: "…into one tidy
   dataset" (held 3 s). Tools and mice fade, leaving the cube.

Segment 2 (clean_viz), `scenes/s02_clean_viz.py` (~22 s). Uses the DLC EPM
sample over 240–260 s, cleaned with the movement applications poster's
pipeline (confidence ≥ 0.99, rolling median 9, linear gaps ≤ 5), so the
trajectory matches the poster's panel:

1. Cube shrinks left; an unlabelled arrow grows from it. The EPM video
   (cropped to the maze, 3×, ~6.7 s, raw 8-keypoint skeleton in orange,
   credited "Data: Loukia Katsouri") plays where the trajectory plot's maze
   will be, while the tail tip's raw x/y trace unfolds in step beside it,
   in the occupancy plot's slot: "Plot keypoint positions over time".
2. When the clip ends, the cleaned trace (teal, drawn over the raw one so
   only the outliers show orange) sweeps across in 1.5 s: "Drop outliers,
   smooth and interpolate tracks". The trace plot is three matplotlib
   layers (axes, raw, cleaned) revealed column by column.
3. Clip and traces crossfade (1.2 s) into the static `plot_centroid_trajectory`
   figure (centroid of centre, tailbase and ears), "Centroid trajectory":
   "Visualise trajectories"; then the `plot_occupancy` subplot (whole
   recording, turbo) appears: "… and occupancy heatmaps" (held 3 s).
4. Everything but the header, cube and arrow fades.

Tried and dropped: raw vs clean videos side by side, snout trails over the
video, raw/clean trails overlaid; at booth distance the cleaning didn't
read. The tail tip shows it best (single-frame spikes, a 2 s jump).

Segment 3 (quantify), `scenes/s03_quantify.py` (~15 s):

1. The bee clip (49–57 s of `sleap_data/bees…`, 2× speed, green/orange
   skeletons) plays large, roughly over where the speed and distance plots
   will be, credited "Data: Pereira et al., Nature Methods, 2022". Caption
   for the whole segment (wording still open): "Quantify motion any way
   you like".
2. The clip shrinks to a thumbnail below the cube as the speed (px/s) and
   inter-bee distance (px) panels appear; then the head-direction polar
   histograms (antenna bases as left/right pair, 30° bins), all from
   movement + xarray plotting. Fades to the header alone, which segment 4
   starts from.

Plots and logo bitmaps are rendered/resampled to their exact on-screen pixel
size (`screen_pixels`, `image`) to avoid aliasing; final renders need
`-qh --fps 30`. No 1080p render has been made of the current version yet.

Segment 4 (gui), `scenes/s04_gui.py` (~27 s):

1. From the header alone: Python logo on the left, "You can call movement
   from Python scripts"; a playing thumbnail of the GUI screen recording
   appears right: "…or use our GUI" (no napari logo; the
   recording itself is the GUI).
2. The thumbnail grows to its place as the Python logo fades and the
   background fades to black (the header stays on top). The recording
   plays at 1.6× (no audio), as large as fits between header and caption,
   with light grey (`#dddddd`) captions at recording times 0 s
   "Interactively explore motion tracks", 10 s (zoom-in) "Identify and
   fix tracking errors", 24 s (ROI panel opens) "Define regions of
   interest". Fades back to white with the header alone, which
   segment 5 starts from.


Segment 5 (community), `scenes/s05_community.py` (~22 s), the last:

1. One slide built up row by row, the caption changing with each row:
   GitHub mark (Font Awesome) and Octicons scales labelled "GitHub" and
   "BSD-3-Clause": "Free and open source"; NIU icon with "Neuroinformatics
   Unit" and the SWC logo: "Developed by a dedicated team of engineers";
   UCL, PDN, Wellcome, Gatsby (SWC is already above): "Supported by our
   host institutes and funders". Small Font Awesome credit bottom right.
2. Rolling credits: "…and a growing community of contributors"; all
   names from the People page (GitHub handles where no name is listed),
   alphabetical, three columns, between soft white masks; no count.
3. As the credits fade, the logo returns from the corner to the title
   card's size and place (the header URL stays): the last frame is the
   first frame, so the video loops seamlessly.

## Next

- Settle the segment 3 caption wording.
- Use the space freed by the header: enlarge content between header and
  caption.
- Remove the netCDF icon if it stays unused.
- Final 1080p30 render of all segments.

## Notes

- movement's `savgol_filter` needs `mode="nearest"` with SciPy >= 1.17 when
  edge windows contain NaNs (worth an upstream issue).
