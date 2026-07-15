`movement-figures`: reproducible figures for research outputs related to the
[`movement` Python package](https://movement.neuroinformatics.dev/).

Each figure is generated via a Quarto document under `figures/`, sharing a
single plotting style from the `movement_figures` package.

The rendered gallery is published at
[neuroinformatics.dev/movement-figures](https://neuroinformatics.dev/movement-figures/).

## Setup

Requires [uv](https://docs.astral.sh/uv/) and the
[Quarto CLI](https://quarto.org/docs/get-started/).

Clone the repo and navigate into it:

```bash
git clone https://github.com/neuroinformatics-unit/movement-figures
cd movement-figures
``` 

Install dependencies and set up the environment with:

```bash
uv sync
```

## Figures

Each figure is a self-contained Quarto document under `figures/`—one `.qmd` per
figure—and they all share execution settings from `figures/_metadata.yml`.

The reusable plotting style and helpers live in the
`movement_figures` package under `src/`, so every figure looks consistent.

The `index.qmd` and `_quarto.yml` at the repo root assemble the rendered figures
into the published gallery.

To render the gallery locally, run:

```bash
uv run quarto preview                  # live-reload while authoring one figure
uv run quarto render                   # build all figures + the gallery
```

The rendered gallery is written to `_site/` and can be opened in a browser
by double-clicking `_site/index.html`.

Vector exports (`pdf` + `svg`) are written to `outputs/` and committed; the
rendered figure gallery website (`_site/`) and caches are not.

## Figure data sources

Figures may draw on two data sources:

- **movement sample data**: the primary source for most inputs, and the only
  option for large files (tracks, videos). Figures fetch these via
  [movement.sample_data](https://movement.neuroinformatics.dev/latest/api/movement.sample_data.html)
  in their code cells, and each `.qmd` declares its datasets in Quarto frontmatter:

  ```yaml
  sample_data:
    - filename: DLC_single-mouse_EPM.predictions.h5
      with_video: true
  ```

  The `prefetch-sample-data` helper reads these declarations and downloads
  everything up front, so a render finds the data already cached:

  ```bash
  uv run prefetch-sample-data
  ```

- **The `data/` folder in this repo**: for *small* files only (< 500 KB), such
  as the ROI coordinates. This folder is git-tracked, so
  anything large would bloat the repo. Access it from a figure
  via `movement_figures.data_dir()`.


## Adding a figure

- Copy an existing `.qmd` file in `figures/`;
- Pick a target `medium`: `manuscript`, `poster`, or `presentation` for `apply_style`;
- Adapt the `.qmd` frontmatter and source to fetch/process necessary data and build the figure;
- End with `save_figure(fig, "<name>")`
- Run `uv run quarto render` and inspect the new files in `outputs/` or the whole gallery in `_site/index.html`.

## Fonts

The fonts used by the figures—Liberation Sans (all media) and Barlow
(posters)—are bundled under `src/movement_figures/fonts/` and registered with
matplotlib by `apply_style`. Nothing needs to be installed system-wide, and
figures render identically on every machine and on CI. Both are licensed under
the SIL Open Font License; see the `LICENSE-*` files alongside them.

## Development

Code quality is enforced with [ruff](https://docs.astral.sh/ruff/) (linting and
formatting), [codespell](https://github.com/codespell-project/codespell), and a
set of [pre-commit](https://pre-commit.com/) hooks (`uv sync` installs all of
these into the environment).

Install the git hook once, so the checks run automatically on every commit:

```bash
uv run pre-commit install
```

After that, committing runs the hooks against your staged files. To run every
hook across the whole repo on demand:

```bash
uv run pre-commit run --all-files
```

Generated figures under `outputs/` are excluded from the hooks so their
committed vector files stay byte-stable across re-renders.

**NOTE:** `ruff` only lints `.py` files—the Python inside `figures/*.qmd` code cells is
not checked for now. Keep figure code tidy by hand, or factor reusable logic
into `src/movement_figures/` where it is linted.

Every pull request re-renders the site as a CI check that all figures still
build, and every merge to `main` redeploys the gallery to GitHub Pages (see
`.github/workflows/render_and_deploy.yml`).
