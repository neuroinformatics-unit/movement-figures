# movement-figures — Project Structure Design

**Date:** 2026-06-29
**Status:** Approved

## Purpose

Provide a reproducible, uniformly-styled home for figures supporting research
outputs (manuscripts, posters, presentations) related to the
[movement](https://movement.neuroinformatics.dev/) Python package. Each figure is
authored as a self-contained Quarto document, all figures share a single plotting
style, and the whole set builds with one command.

## Key Decisions

| Decision | Choice |
|----------|--------|
| Figure organization | Flat — one `.qmd` per figure under `figures/` |
| Data sources | `movement.sample_data` (pooch-cached) + inline synthetic generators |
| Style enforcement | Shared installable package `movement_figures`: a base mplstyle + per-medium override styles, composed at apply time |
| Export formats | Vector PDF + SVG; plus rendered Quarto pages as a browsable gallery |
| Committed artifacts | Final figures in `outputs/` are committed; `_site/`, caches gitignored |
| Dependency management | uv (`pyproject.toml` + `uv.lock`) |
| Python version | `>=3.12,<3.15` (range supported by movement 0.17) |
| Build backend | setuptools (matches movement); static version |
| Package layout | `src/` layout, package/import name `movement_figures` |

## Directory Structure

```
movement-figures/
├── _quarto.yml              # global Quarto project config (website/gallery),
│                            #   shared execution + format defaults
├── pyproject.toml           # uv-managed: deps + local movement_figures package
├── uv.lock
├── index.qmd                # gallery landing page; lists the figures
├── figures/                 # FLAT — one .qmd per figure
│   ├── _metadata.yml        #   shared front-matter defaults for all figures
│   ├── pose_tracks.qmd      #   (example figure)
│   └── ...
├── src/movement_figures/    # installable style + helper package (src layout)
│   ├── __init__.py          #   re-exports apply_style, save_figure, PALETTE, FIGSIZES
│   ├── style.py             #   apply_style(medium=...), PALETTE, FIGSIZES
│   ├── styles/              #   layered matplotlib style sheets
│   │   ├── movement-base.mplstyle        # shared look (fonts, colors, spines…)
│   │   ├── movement-manuscript.mplstyle  # medium overrides: fontsize, linewidth
│   │   ├── movement-poster.mplstyle
│   │   └── movement-presentation.mplstyle
│   └── io.py                #   save_figure() → vector PDF+SVG into outputs/
├── outputs/                 # COMMITTED publication-ready SVG/PDF exports
├── README.md
└── .gitignore               # _site/, .quarto/, pooch cache, __pycache__, etc.
```

## Components

### `movement_figures` package (style + helpers)

The uniform-style enforcer, installed editable via uv so style edits propagate
without reinstall.

- **`styles/` (layered mplstyle sheets)** — the look is split so the shared
  identity lives in one place and only medium-specific parameters vary:
  - `movement-base.mplstyle` — the single source of truth for the shared look:
    font family, colors, tick/spine defaults, savefig DPI/format defaults.
  - `movement-<medium>.mplstyle` — thin override sheets (`manuscript`, `poster`,
    `presentation`) that set only what differs by medium: font sizes, line
    widths, marker sizes. Each contains just the few keys it changes.
- **`style.py`** — `apply_style(medium="manuscript")` composes the styles by
  applying `[base, <medium>]` in order (matplotlib applies them left-to-right, so
  the medium sheet overrides the base). `medium` defaults to `"manuscript"` and
  is validated against the available sheets. Also exposes what a style sheet
  cannot: `PALETTE` (named colors aligned with movement branding) and `FIGSIZES`
  (named figure dimensions per medium, e.g. single-column, double-column,
  poster).
- **`io.py`** — `save_figure(fig, name, formats=("pdf", "svg"))` writes vector
  files to `outputs/` with consistent naming derived from `name`.
- **`__init__.py`** — re-exports `apply_style`, `save_figure`, `PALETTE`,
  `FIGSIZES` for a one-line import in each figure.

**Usage contract** (every figure):
```python
from movement_figures import apply_style, save_figure, PALETTE, FIGSIZES
apply_style(medium="manuscript")  # or "poster" / "presentation"
# ... build `fig` ...
save_figure(fig, "pose_tracks")
```

### Figures (`figures/*.qmd`)

One Quarto document per figure. Each: loads/generates data, applies the shared
style, builds the plot, and calls `save_figure`. `figures/_metadata.yml` holds
front-matter defaults (jupyter engine, code-fold, figure format) so individual
documents stay minimal.

### Quarto project (`_quarto.yml`, `index.qmd`)

A Quarto *website project* so `quarto render` builds every figure at once into a
browsable gallery. `_quarto.yml` sets shared execution and format defaults
inherited by all documents. `index.qmd` is the landing page listing the figures.

### Data flow

- **Sample data:** `movement.sample_data` fetches/caches public datasets via
  pooch into a gitignored cache. Reproducible from code; nothing committed.
- **Synthetic data:** generated inline within a figure's `.qmd` for
  illustrative/schematic figures.

No data files are committed.

## Build Workflow

- `uv sync` — create/refresh the locked environment.
- `uv run quarto preview` — live-reload while authoring a single figure.
- `uv run quarto render` — build all figures + the gallery. Running Quarto under
  `uv run` guarantees it uses the locked environment.

## Git Strategy

- **Tracked:** source `.qmd`, the `movement_figures` package, project config, and
  final `outputs/*.{pdf,svg}`.
- **Ignored:** `_site/`, `.quarto/`, pooch cache, `__pycache__/`, notebook
  checkpoints.

## Out of Scope (YAGNI)

- High-DPI PNG export — trivially added later to `save_figure`'s `formats`.
- Per-output (manuscript/poster) grouping — flat layout chosen; revisit only if
  venue-specific restyling becomes a real need.
- Committed precomputed/heavy intermediate results — not needed while data is
  sample-data + synthetic.
- CI publishing to GitHub Pages — can be layered on later without structural
  change.

## Testing / Verification

The build itself is the test: `uv run quarto render` must complete with all
figures producing their `outputs/` files. A clean checkout + `uv sync` +
`quarto render` reproduces every figure from source.
