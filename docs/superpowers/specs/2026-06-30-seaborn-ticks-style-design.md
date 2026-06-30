# Seaborn-Style Restyle + Set2 Brand Palette — Design

**Date:** 2026-06-30
**Status:** Approved
**Branch:** `seaborn-ticks-style` (off `pupil-poster-figure`)

## Purpose

Restyle the shared `movement_figures` look to match seaborn's `ticks` axes style
and `poster` context, use the 'Barlow' font for the poster medium, and adopt
ColorBrewer **Set2** as the brand color cycle with a revised, Set2/Dark2/Pastel2
semantic `PALETTE`. Style param values are baked statically into the mplstyle
sheets and `style.py`; seaborn is added as a runtime dependency so figures can
call `despine(trim=True)` themselves.

## Key Decisions

| Decision | Choice |
|----------|--------|
| Ticks look scope | All media → `movement-base.mplstyle` |
| Spines | Despine top/right (left + bottom only) |
| Base colors | seaborn grey `0.15` for text/labels/edges/ticks (replaces `#333333`) |
| Base font | `font.sans-serif: Arial, DejaVu Sans, Liberation Sans, Bitstream Vera Sans, sans-serif` |
| Color cycle | `axes.prop_cycle` = Set2 (8 colors) in base |
| Poster context | seaborn `poster` font sizes + line/tick widths in `movement-poster.mplstyle` |
| Poster font | `font.sans-serif: Barlow, DejaVu Sans, sans-serif` (Barlow first, graceful fallback) |
| Brand constant | new `SET2` tuple exported from `movement_figures` |
| PALETTE | revised (scheme B + Dark2 magenta accent); keys gain `highlight`, `ink` |
| Centroid marker | `PALETTE["highlight"]`, `marker="x"`, `s=220`, `linewidths=4` |
| Despine | each figure calls `seaborn.despine(fig=fig, trim=True)` explicitly (NOT inside `save_figure`) |
| seaborn dependency | added as a runtime dep — figures import it for `despine(trim=True)` (style param values are still copied statically into the mplstyle sheets) |
| Output quality (base) | `pdf.fonttype: 42`, `ps.fonttype: 42`, `svg.fonttype: none`, `savefig.dpi: 300` — embedded/editable fonts, high DPI |

## Color values

`SET2` (= base `axes.prop_cycle`, ColorBrewer Set2):

```
#66c2a5  #fc8d62  #8da0cb  #e78ac3  #a6d854  #ffd92f  #e5c494  #b3b3b3
```

`PALETTE` (revised):

| key | hex | source |
|-----|-----|--------|
| `primary` | `#66c2a5` | Set2 teal |
| `secondary` | `#fc8d62` | Set2 orange |
| `accent` | `#e7298a` | Dark2 magenta (vivid; replaces the old near-invisible `#264653`) |
| `muted` | `#b3b3b3` | Set2 grey |
| `highlight` | `#f4cae4` | Pastel2 pink (light marks on dark backgrounds, e.g. the centroid) |
| `ink` | `#666666` | Dark2 grey (dark neutral) |

## Components

### `src/movement_figures/styles/movement-base.mplstyle` (rewritten)

The seaborn `ticks` look, despined, with the Set2 cycle:

```
figure.facecolor: white
axes.facecolor: white
axes.edgecolor: 0.15
axes.labelcolor: 0.15
axes.axisbelow: True
axes.grid: False
axes.spines.top: False
axes.spines.right: False
axes.spines.left: True
axes.spines.bottom: True
text.color: 0.15
xtick.color: 0.15
ytick.color: 0.15
xtick.direction: out
ytick.direction: out
xtick.top: False
ytick.right: False
xtick.bottom: True
ytick.left: True
lines.solid_capstyle: round
font.family: sans-serif
font.sans-serif: Arial, DejaVu Sans, Liberation Sans, Bitstream Vera Sans, sans-serif
axes.prop_cycle: cycler('color', ['66c2a5', 'fc8d62', '8da0cb', 'e78ac3', 'a6d854', 'ffd92f', 'e5c494', 'b3b3b3'])
savefig.dpi: 300
savefig.bbox: tight
savefig.transparent: False
pdf.fonttype: 42
ps.fonttype: 42
svg.fonttype: none
```

The font-type settings guarantee high-quality, editable output: `pdf.fonttype`/`ps.fonttype`
`42` embed TrueType (Type42) fonts so text stays selectable/editable in PDF/PS,
and `svg.fonttype: none` keeps SVG text as real `<text>` elements (referencing the
font by family) instead of outlined paths. These remain deterministic under the
already-pinned `svg.hashsalt` + suppressed timestamps.

Notes: seaborn's `image.cmap: rocket` is intentionally NOT adopted (figures set
`cmap` explicitly; keep matplotlib's default). The per-medium sheets still set
their own `font.size`, so base sets none.

### `src/movement_figures/styles/movement-poster.mplstyle` (rewritten)

seaborn `poster` context + Barlow:

```
font.sans-serif: Barlow, DejaVu Sans, sans-serif
font.size: 24
axes.titlesize: 24
axes.labelsize: 24
xtick.labelsize: 22
ytick.labelsize: 22
legend.fontsize: 22
legend.title_fontsize: 24
axes.linewidth: 2.5
grid.linewidth: 2
lines.linewidth: 3.0
lines.markersize: 12
patch.linewidth: 2
xtick.major.width: 2.5
ytick.major.width: 2.5
xtick.minor.width: 2
ytick.minor.width: 2
xtick.major.size: 12
ytick.major.size: 12
xtick.minor.size: 8
ytick.minor.size: 8
```

`font.family` stays `sans-serif` (from base); the poster `font.sans-serif`
override puts Barlow first with a DejaVu fallback so renders never break where
Barlow is absent (Barlow is confirmed installed locally at
`~/Library/Fonts/Barlow-Regular.ttf`).

### `movement-manuscript.mplstyle` / `movement-presentation.mplstyle`

Unchanged values; they inherit the new base look (per the all-media choice).

### `src/movement_figures/style.py`

- Add `SET2: tuple[str, ...]` = the 8 Set2 hex strings (the brand palette, matching
  the base cycle).
- Replace the `PALETTE` dict values with the revised table above (same dict type;
  keys now `primary`, `secondary`, `accent`, `muted`, `highlight`, `ink`).
- `FIGSIZES`, `AVAILABLE_MEDIA`, `apply_style` unchanged.

### `src/movement_figures/__init__.py`

Add `SET2` to the imports and `__all__`.

### `src/movement_figures/io.py`

Unchanged — despine is applied per-figure, not here.

### `pyproject.toml`

Add `seaborn` to `[project].dependencies` (figures import it for `despine`).

### `figures/pupil_tracking_poster.qmd`

- Centroid marker changes: `color=PALETTE["highlight"]`, `s=220`, `linewidths=4`
  (thicker, light). Keypoints already pick up Set2 automatically via the cycle.
- Add `import seaborn as sns` (imports cell) and call
  `sns.despine(fig=fig, trim=True)` after both panels are built, before
  `save_figure`. `trim` shortens the velocity panel's left/bottom spines to their
  first/last tick; the image panel has no ticks, so seaborn leaves it untouched.

Every figure that wants the trimmed look calls `sns.despine(fig=fig, trim=True)`
itself — this is the per-figure convention going forward (also applies when the
example figure is updated, if desired; out of scope to retrofit here beyond the
re-render).

## Tests (`tests/test_style.py`)

- Update `test_apply_style_poster_fontsize`: assert `font.size == 24` (was 18).
- Add `test_apply_style_color_cycle_matches_set2`: after `apply_style("poster")`
  (or any medium), `plt.rcParams["axes.prop_cycle"].by_key()["color"]` equals
  `list(SET2)` — ties the mplstyle cycle to the `SET2` constant so they cannot
  drift.
- Add a check that `set(PALETTE) == {"primary","secondary","accent","muted","highlight","ink"}`.
- Existing assertions (`axes.spines.top is False`, manuscript `font.size == 8`,
  `FIGSIZES`/media shape, `PALETTE` is a dict) still hold.

No new `tests/test_io.py` tests are needed — `save_figure` is unchanged. Despine
is exercised by rendering the pupil figure, not by a unit test.

## Knock-on / Verification

- Re-render and re-commit BOTH committed figures, whose outputs change under the
  new style:
  - `outputs/example_trajectory.{pdf,svg}` (manuscript; base look + cycle change),
  - `outputs/pupil_tracking_poster.{pdf,svg}` (poster context + Barlow + centroid).
- `uv run pytest -q` passes (with the updated/added style tests).
- `uv run quarto render` builds the whole gallery cleanly.
- Re-rendering a second time produces no `outputs/` diff (determinism holds —
  `save_figure` already suppresses timestamps and pins the SVG hash salt).
- `.superpowers/` is added to `.gitignore` (SDD + brainstorm scratch).

## Out of Scope

- No change to `apply_style`'s signature or the `manuscript`/`presentation` font
  sizes.
- `image.cmap: rocket` and other seaborn brand defaults beyond the `ticks` axes
  look are not adopted (seaborn is imported only for `despine`; `sns.set_theme`
  is never called, so it does not touch rcParams).
