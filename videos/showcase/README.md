# movement showcase video

A silent, looping video (~110 s) that showcases `movement` to passers by.
It was first made to be shown at the NWB/DANDI booth at SfN 2026.
There is no audio; captions are used instead. Animations are made with manim,
based on real tracking data, and plots are made with `movement`'s or `xarray`'s
own plotting functions.

Output: 1920×1080 at 30 fps, as
`media/movement_showcase_<YYYY-MM-DD>_<resolution>.mp4`.

## What it shows

The story is "many tools in, one dataset out", then what you can do with
that dataset. It runs in five segments, each a manim scene in `scenes/`:

| #   | Module             | Scene       | Content |
| --- | ------------------ | ----------- | ------- |
| 1   | `s01_io.py`        | `IO`        | Title card. A mouse video turns into its tracked skeleton. Logos of supported tools (DeepLabCut, SLEAP, Lightning Pose, NWB, "and more…") appear as three skeleton mice run towards a data cube: one tidy dataset. |
| 2   | `s02_clean_viz.py` | `CleanViz`  | A mouse in an elevated plus maze, with the raw trace of its tail tip, then the trace cleaned (outliers dropped, smoothed, gaps interpolated). Then a centroid trajectory and an occupancy heatmap. |
| 3   | `s03_quantify.py`  | `Quantify`  | Two interacting bees, then their speeds, the distance between them, and head-direction histograms. |
| 4   | `s04_gui.py`       | `GUI`       | movement from Python scripts, then a screen recording of the napari GUI: exploring tracks, fixing tracking errors, drawing regions of interest. |
| 5   | `s05_community.py` | `Community` | Open source (GitHub, BSD-3-Clause), the team (NIU, SWC), host institutes and funders, then rolling credits for all contributors. |

The segments are rendered separately and joined end to end. Each one starts
on the exact frame the previous one ends on, and the last frame equals the
first, so the video loops seamlessly.

## Design conventions

Keep these in mind when editing, so the video stays readable from a few
metres away by someone walking past:

- **One thing at a time.** Big, short captions; one element to look at;
  restrained animation (things appear rather than fly in).
- **Consistent captions.** Every caption change uses `caption_change`: the
  old one fades out before the new one rises in.
- **A persistent header.** The URL (centre right) and the logo (top right)
  stay on screen throughout, so any glance identifies the project.
- **Brand.** White background, Barlow typeface, ColorBrewer Set2 colours.
- **Truthful plots.** Plots use movement's (or xarray's) own matplotlib
  plotting functions with their default look; only font sizes, axes and
  colours are adjusted.
- **Credits.** Videos clips carry a small-print data
  credit below it when they are first shown. Icons from third-party libraries
  are also credited on screen.
- **No aliasing.** Plots and logos are rendered or resampled to their exact
  on-screen pixel size, so fine lines and text stay sharp.

## Building the video

### Requirements

See the [main README](../../README.md#Videos).

### Inputs

The video draws on three kinds of input:

- **movement sample data**, fetched automatically: the DeepLabCut
  DBTravelator mouse (segment 1) and elevated plus maze mouse (segment 2),
  with their videos.
- **Committed files** in `assets/`: the movement and NIU logos, and three
  icons: Font Awesome's `file-solid-full.svg` and `github-brands.svg`
  (CC BY 4.0) and GitHub Octicons' `octicon-law-24.svg` (MIT), credited on
  screen.
- **Files that can't be committed** (third-party logos, the SLEAP bees
  recording, the napari screen recording), which you put in `inputs/` by
  hand.

`video.yml` lists every file in `inputs/`, with where to get it, who to
credit, and its sha256 hash. Check that yours are complete and identical to
the ones last used:

```bash
uv run movement-video check videos/showcase
```

A file reported as `changed` differs from the recorded one. That's fine if
you replaced it on purpose; record the new hash with
`uv run movement-video update-hashes videos/showcase`.

Logos are shown as they are, except that opaque ones (logos on a white
canvas) are made transparent and trimmed. Trim transparent logos to their
visible content before adding them.

### Rendering

```bash
uv run movement-video render videos/showcase                     # 720p draft
uv run movement-video render videos/showcase --resolution 1080p  # final
```

`render` checks the inputs, fetches the sample data, renders each segment,
and joins them into one mp4 in `media/`. While working on one segment, render
just that one (it isn't joined):

```bash
uv run movement-video render videos/showcase --segment s02_clean_viz
```

The first render of each segment derives data into `cache/` (cleaned tracks,
video frames, plot images at the render's pixel size). Delete `cache/` to
rebuild it, e.g. after changing how data are processed.

## Making a new version

1. Edit the scenes, and replace any inputs (then run `update-hashes`).
2. Refresh the contributor credits from movement's People page:
   `uv run python videos/showcase/scenes/community.py`. The diff of
   `contributors.txt` shows who was added.
3. Render at 1080p and review it.
4. Commit, tag the commit `showcase-<YYYY-MM-DD>`, and publish a GitHub
   Release for the tag with the 1080p mp4 attached.

The tag pins everything needed to rebuild that version: the scenes, the
locked environment (`uv.lock`), the input hashes and the credits.

## How it's put together

```
videos/showcase/
  video.yml          segments, sample data, and the manifest of inputs/
  contributors.txt   names for the rolling credits (committed)
  assets/            committed images
  inputs/            files that aren't committed (you provide these)
  scenes/            manim code
  cache/, media/     derived data and renders (not committed)
```

In `scenes/`:

- `s01_io.py` … `s05_community.py`: the five scenes.
- `common.py`: paths, colours, layout positions shared
  across segments, plus the tool rows, the isometric data cube and its labels.
  It re-exports the brand, caption and header helpers from `movement_figures.video`.
- `mouse.py`: skeletons and video frames from the DBTravelator mouse. The
  three running mice are one track replayed with different gait phases.
- `clean_viz_data.py`, `clean_viz_plots.py`: the plus-maze data, its cleaning
  and its plots.
- `bees.py`, `bee_plots.py`: the bee tracks, their metrics and plots.
- `community.py`: reads `contributors.txt`, and refreshes it when run.

## Data credits

- DBTravelator mouse: Holly Morley.
- Elevated plus maze mouse: Loukia Katsouri.
- Bees: Pereira et al., *Nature Methods*, 2022.
