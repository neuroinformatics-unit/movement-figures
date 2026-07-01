# movement-figures

Reproducible figures for research outputs related to
[`movement` Python package](https://movement.neuroinformatics.dev/).

Each figure is generated via a Quarto document under `figures/`, sharing a
single plotting style from the `movement_figures` package.

## Setup

Requires [uv](https://docs.astral.sh/uv/) and the
[Quarto CLI](https://quarto.org/docs/get-started/).

Install dependencies and set up the environment with:

```bash
uv sync
```

## Building figures

```bash
uv run quarto preview                  # live-reload while authoring one figure
uv run quarto render                   # build all figures + the gallery
```

Vector exports (`pdf` + `svg`) are written to `outputs/` and committed; the
rendered figure gallery website (`_site/`) and caches are not.

## Adding a figure

- Copy an existing `.qmd` file in `figures/`;
- Pick a target `medium`: `manuscript`, `poster`, or `presentation` for `apply_style`;
- Adapt the `.qmd` source to fetch/process necessary data and build the figure;
- End with `save_figure(fig, "<name>")`
- Run `uv run quarto render` and inspect the new files in `outputs/` or the whole gallery in `_site/index.html`.

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

> [!NOTE]
> ruff only lints `.py` files—the Python inside `figures/*.qmd` code cells is
> not checked for now. Keep figure code tidy by hand, or factor reusable logic
> into `src/movement_figures/` where it is linted.
