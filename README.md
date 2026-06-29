# movement-figures

Reproducible figures for research outputs related to
[movement.neuroinformatics.dev](https://movement.neuroinformatics.dev/).

Each figure is generated via a Quarto document under `figures/`, sharing a
single layered plotting style from the `movement_figures` package.

## Setup

Requires [uv](https://docs.astral.sh/uv/) and the
[Quarto CLI](https://quarto.org/docs/get-started/).

```bash
uv sync
```

## Building figures

```bash
uv run quarto preview                  # live-reload while authoring one figure
uv run quarto render                   # build all figures + the gallery
```

Vector exports (`pdf` + `svg`) are written to `outputs/` and committed; the
rendered site (`_site/`) and caches are not.

## Adding a figure

Copy `figures/example_trajectory.qmd`, pick a `medium`
(`manuscript` / `poster` / `presentation`) for `apply_style`, build the plot,
and end with `save_figure(fig, "<name>")`.
