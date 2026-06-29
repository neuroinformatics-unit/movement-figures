# movement-figures Project Structure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold a uv-managed, Quarto-based repository where each research figure is a flat `.qmd` document sharing one layered, medium-aware matplotlib style.

**Architecture:** A `src/`-layout installable package (`movement_figures`) holds the style sheets and helpers (`apply_style`, `save_figure`, `PALETTE`, `FIGSIZES`). Figures live flat under `figures/`, each importing the package and exporting vector files to `outputs/`. A Quarto website project ties everything together so `uv run quarto render` builds all figures plus a browsable gallery.

**Tech Stack:** Python 3.12–3.14, uv, setuptools, matplotlib, numpy, movement ≥0.17, Quarto (jupyter engine), pytest.

## Global Constraints

- Python `>=3.12,<3.15` (`requires-python` in `pyproject.toml`) — the range supported by movement 0.17.
- Dependencies managed exclusively with uv; commit `uv.lock`.
- Package/import name: `movement_figures`; `src/` layout.
- Figure organization: flat — one `.qmd` per figure under `figures/`.
- Export formats: vector `pdf` + `svg` (no PNG).
- `apply_style(medium=...)` composes `[movement-base, movement-<medium>]`; media are `manuscript` (default), `poster`, `presentation`.
- Git: track source `.qmd`, the package, config, and final `outputs/*.{pdf,svg}`; ignore `_site/`, `.quarto/`, caches, `.venv/`.
- **Prerequisite (not installable via uv):** the Quarto CLI must be installed on the system — https://quarto.org/docs/get-started/. Verify with `quarto --version`.

---

### Task 1: uv project + package skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `src/movement_figures/__init__.py`
- Create: `tests/test_package_imports.py`

**Interfaces:**
- Consumes: nothing.
- Produces: an installed, importable `movement_figures` package and a working `uv` environment with `pytest` available in the `dev` group.

- [ ] **Step 1: Write `pyproject.toml`**

```toml
[project]
name = "movement-figures"
version = "0.1.0"
description = "Reproducible figures for movement research outputs"
readme = "README.md"
requires-python = ">=3.12,<3.15"
dependencies = [
    "movement>=0.17",
    "matplotlib",
    "numpy",
    "jupyter",
    "nbformat",
    "nbclient",
]

[build-system]
requires = ["setuptools>=64"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
movement_figures = ["styles/*.mplstyle"]

[dependency-groups]
dev = ["pytest"]
```

> Build backend is setuptools to match the movement package. Version is kept
> static here (movement uses `setuptools_scm`); this repo is not released/tagged,
> so dynamic git-tag versioning would add friction without benefit. The
> `package-data` entry ensures the `.mplstyle` sheets ship with the package.

- [ ] **Step 2: Create the package init**

`src/movement_figures/__init__.py`:

```python
"""Shared style and helpers for movement research figures."""

__all__ = []
```

- [ ] **Step 3: Write the failing test**

`tests/test_package_imports.py`:

```python
def test_package_importable():
    import movement_figures

    assert movement_figures.__doc__ is not None
```

- [ ] **Step 4: Sync the environment**

Run: `uv sync`
Expected: creates `.venv/`, writes `uv.lock`, installs deps and the editable `movement_figures` package.

- [ ] **Step 5: Run the test to verify it passes**

Run: `uv run pytest tests/test_package_imports.py -v`
Expected: PASS (1 passed).

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml uv.lock src/movement_figures/__init__.py tests/test_package_imports.py
git commit -m "feat: scaffold uv project and movement_figures package"
```

---

### Task 2: Layered, medium-aware style

**Files:**
- Create: `src/movement_figures/styles/movement-base.mplstyle`
- Create: `src/movement_figures/styles/movement-manuscript.mplstyle`
- Create: `src/movement_figures/styles/movement-poster.mplstyle`
- Create: `src/movement_figures/styles/movement-presentation.mplstyle`
- Create: `src/movement_figures/style.py`
- Modify: `src/movement_figures/__init__.py`
- Create: `tests/test_style.py`

**Interfaces:**
- Consumes: the installed package from Task 1.
- Produces:
  - `apply_style(medium: str = "manuscript") -> None` — composes base + medium sheets; raises `ValueError` on unknown medium.
  - `AVAILABLE_MEDIA: tuple[str, ...] = ("manuscript", "poster", "presentation")`
  - `PALETTE: dict[str, str]` — named hex colors.
  - `FIGSIZES: dict[str, dict[str, tuple[float, float]]]` — `{medium: {name: (w_in, h_in)}}`.

- [ ] **Step 1: Create the base style sheet**

`src/movement_figures/styles/movement-base.mplstyle`:

```
figure.facecolor: white
axes.facecolor: white
axes.edgecolor: 333333
axes.labelcolor: 333333
axes.spines.top: False
axes.spines.right: False
axes.grid: False
text.color: 333333
xtick.color: 333333
ytick.color: 333333
font.family: sans-serif
savefig.dpi: 300
savefig.bbox: tight
savefig.transparent: False
```

- [ ] **Step 2: Create the per-medium override sheets**

`src/movement_figures/styles/movement-manuscript.mplstyle`:

```
font.size: 8
axes.titlesize: 9
axes.labelsize: 8
lines.linewidth: 1.0
lines.markersize: 4
```

`src/movement_figures/styles/movement-poster.mplstyle`:

```
font.size: 18
axes.titlesize: 22
axes.labelsize: 18
lines.linewidth: 2.5
lines.markersize: 9
```

`src/movement_figures/styles/movement-presentation.mplstyle`:

```
font.size: 14
axes.titlesize: 16
axes.labelsize: 14
lines.linewidth: 2.0
lines.markersize: 7
```

- [ ] **Step 3: Write the failing test**

`tests/test_style.py`:

```python
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest

from movement_figures import AVAILABLE_MEDIA, FIGSIZES, PALETTE, apply_style


def test_available_media():
    assert AVAILABLE_MEDIA == ("manuscript", "poster", "presentation")


def test_apply_style_sets_medium_fontsize():
    apply_style("manuscript")
    assert plt.rcParams["font.size"] == 8
    apply_style("poster")
    assert plt.rcParams["font.size"] == 18


def test_apply_style_keeps_base_params():
    apply_style("presentation")
    assert plt.rcParams["axes.spines.top"] is False


def test_apply_style_default_is_manuscript():
    apply_style()
    assert plt.rcParams["font.size"] == 8


def test_apply_style_rejects_unknown_medium():
    with pytest.raises(ValueError):
        apply_style("billboard")


def test_palette_and_figsizes_shape():
    assert isinstance(PALETTE, dict) and len(PALETTE) >= 1
    assert set(FIGSIZES) == set(AVAILABLE_MEDIA)
    for sizes in FIGSIZES.values():
        for dims in sizes.values():
            assert len(dims) == 2
```

- [ ] **Step 4: Run the test to verify it fails**

Run: `uv run pytest tests/test_style.py -v`
Expected: FAIL with `ImportError` (cannot import `apply_style`).

- [ ] **Step 5: Implement `style.py`**

`src/movement_figures/style.py`:

```python
"""Layered, medium-aware matplotlib styling."""

from importlib.resources import files

import matplotlib.pyplot as plt

AVAILABLE_MEDIA: tuple[str, ...] = ("manuscript", "poster", "presentation")

_STYLE_DIR = files("movement_figures") / "styles"

# Named colors aligned with movement branding (adjust hex values to taste).
PALETTE: dict[str, str] = {
    "primary": "#2a9d8f",
    "secondary": "#e76f51",
    "accent": "#264653",
    "muted": "#8d99ae",
}

# Figure dimensions in inches, per medium.
FIGSIZES: dict[str, dict[str, tuple[float, float]]] = {
    "manuscript": {"single": (3.5, 2.6), "double": (7.0, 4.0)},
    "poster": {"single": (8.0, 6.0), "double": (16.0, 9.0)},
    "presentation": {"single": (6.0, 4.0), "double": (12.0, 6.75)},
}


def apply_style(medium: str = "manuscript") -> None:
    """Apply the shared base style plus a medium-specific override.

    Parameters
    ----------
    medium : str
        One of ``AVAILABLE_MEDIA``. Defaults to ``"manuscript"``.

    Raises
    ------
    ValueError
        If ``medium`` is not a known medium.
    """
    if medium not in AVAILABLE_MEDIA:
        raise ValueError(
            f"Unknown medium {medium!r}; choose from {AVAILABLE_MEDIA}."
        )
    base = str(_STYLE_DIR / "movement-base.mplstyle")
    override = str(_STYLE_DIR / f"movement-{medium}.mplstyle")
    plt.style.use([base, override])
```

- [ ] **Step 6: Re-export from the package init**

Replace `src/movement_figures/__init__.py` with:

```python
"""Shared style and helpers for movement research figures."""

from movement_figures.style import (
    AVAILABLE_MEDIA,
    FIGSIZES,
    PALETTE,
    apply_style,
)

__all__ = ["AVAILABLE_MEDIA", "FIGSIZES", "PALETTE", "apply_style"]
```

- [ ] **Step 7: Run the test to verify it passes**

Run: `uv run pytest tests/test_style.py -v`
Expected: PASS (6 passed).

- [ ] **Step 8: Commit**

```bash
git add src/movement_figures/styles src/movement_figures/style.py src/movement_figures/__init__.py tests/test_style.py
git commit -m "feat: add layered medium-aware matplotlib style"
```

---

### Task 3: Vector figure export helper

**Files:**
- Create: `src/movement_figures/io.py`
- Modify: `src/movement_figures/__init__.py`
- Create: `tests/test_io.py`

**Interfaces:**
- Consumes: the installed package from Task 1.
- Produces:
  - `save_figure(fig, name, formats=("pdf", "svg"), output_dir="outputs") -> list[pathlib.Path]`
    — writes `fig` to `<output_dir>/<name>.<fmt>` for each format, creating the
    directory if needed, and returns the written paths.

- [ ] **Step 1: Write the failing test**

`tests/test_io.py`:

```python
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from movement_figures import save_figure


def test_save_figure_writes_pdf_and_svg(tmp_path):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    paths = save_figure(fig, "demo", output_dir=tmp_path)
    names = {p.name for p in paths}
    assert names == {"demo.pdf", "demo.svg"}
    for p in paths:
        assert p.exists() and p.stat().st_size > 0


def test_save_figure_custom_formats(tmp_path):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    paths = save_figure(fig, "demo", formats=("svg",), output_dir=tmp_path)
    assert [p.name for p in paths] == ["demo.svg"]


def test_save_figure_creates_missing_dir(tmp_path):
    target = tmp_path / "nested" / "outputs"
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    save_figure(fig, "demo", output_dir=target)
    assert (target / "demo.pdf").exists()
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/test_io.py -v`
Expected: FAIL with `ImportError` (cannot import `save_figure`).

- [ ] **Step 3: Implement `io.py`**

`src/movement_figures/io.py`:

```python
"""Consistent vector export for figures."""

from collections.abc import Sequence
from pathlib import Path

from matplotlib.figure import Figure


def save_figure(
    fig: Figure,
    name: str,
    formats: Sequence[str] = ("pdf", "svg"),
    output_dir: str | Path = "outputs",
) -> list[Path]:
    """Save ``fig`` as vector files named ``<name>.<fmt>`` in ``output_dir``.

    Returns the list of written paths. Creates ``output_dir`` if absent.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for fmt in formats:
        path = output_dir / f"{name}.{fmt}"
        fig.savefig(path)
        paths.append(path)
    return paths
```

- [ ] **Step 4: Re-export from the package init**

Update `src/movement_figures/__init__.py` to:

```python
"""Shared style and helpers for movement research figures."""

from movement_figures.io import save_figure
from movement_figures.style import (
    AVAILABLE_MEDIA,
    FIGSIZES,
    PALETTE,
    apply_style,
)

__all__ = [
    "AVAILABLE_MEDIA",
    "FIGSIZES",
    "PALETTE",
    "apply_style",
    "save_figure",
]
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `uv run pytest tests/test_io.py -v`
Expected: PASS (3 passed).

- [ ] **Step 6: Commit**

```bash
git add src/movement_figures/io.py src/movement_figures/__init__.py tests/test_io.py
git commit -m "feat: add vector figure export helper"
```

---

### Task 4: Quarto project, gitignore, and first figure

**Files:**
- Create: `_quarto.yml`
- Create: `index.qmd`
- Create: `figures/_metadata.yml`
- Create: `figures/example_trajectory.qmd`
- Create: `.gitignore`
- Modify: `README.md`

**Interfaces:**
- Consumes: `apply_style`, `save_figure`, `PALETTE`, `FIGSIZES` from the package.
- Produces: a buildable Quarto website that renders all figures and a gallery, plus committed vector outputs.

- [ ] **Step 1: Write `.gitignore`**

`.gitignore`:

```
# Quarto / build artifacts
_site/
.quarto/
.jupyter_cache/

# Python
.venv/
__pycache__/
*.py[cod]
.ipynb_checkpoints/
.pytest_cache/

# movement sample-data cache (pooch); outputs/ is committed deliberately
```

- [ ] **Step 2: Write the global Quarto config**

`_quarto.yml`:

```yaml
project:
  type: website
  output-dir: _site

website:
  title: "movement figures"
  description: "Reproducible figures for movement research outputs."

format:
  html:
    theme: cosmo
    code-fold: true
    toc: true

execute:
  freeze: auto
  warning: false
```

- [ ] **Step 3: Write shared figure metadata**

`figures/_metadata.yml`:

```yaml
engine: jupyter
execute:
  echo: true
  warning: false
```

- [ ] **Step 4: Write the gallery landing page**

`index.qmd`:

```markdown
---
title: "movement figures"
listing:
  contents: figures
  type: grid
  sort: "title"
---

Reproducible figures for research outputs related to
[movement](https://movement.neuroinformatics.dev/).
Each card below links to a figure generated from a single Quarto document.
```

- [ ] **Step 5: Write the first example figure**

`figures/example_trajectory.qmd`:

````markdown
---
title: "Example trajectory"
---

A self-contained example figure: a synthetic 2D trajectory, styled and exported
to vector files via the shared `movement_figures` helpers. Use this as the
template for new figures.

```{python}
import numpy as np
import matplotlib.pyplot as plt

from movement_figures import apply_style, save_figure, PALETTE, FIGSIZES

apply_style("manuscript")

rng = np.random.default_rng(0)
steps = rng.normal(size=(200, 2)).cumsum(axis=0)

fig, ax = plt.subplots(figsize=FIGSIZES["manuscript"]["single"])
ax.plot(steps[:, 0], steps[:, 1], color=PALETTE["primary"], lw=1.0)
ax.scatter(*steps[0], color=PALETTE["accent"], zorder=3, label="start")
ax.scatter(*steps[-1], color=PALETTE["secondary"], zorder=3, label="end")
ax.set(xlabel="x (px)", ylabel="y (px)", aspect="equal")
ax.legend(frameon=False)

save_figure(fig, "example_trajectory")
fig
```
````

- [ ] **Step 6: Update the README with build instructions**

Replace `README.md` contents with:

```markdown
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
```

- [ ] **Step 7: Render the example figure to verify the build**

Run: `uv run quarto render figures/example_trajectory.qmd`
Expected: render succeeds; `outputs/example_trajectory.pdf` and
`outputs/example_trajectory.svg` exist.

- [ ] **Step 8: Render the whole project to verify the gallery**

Run: `uv run quarto render`
Expected: render succeeds with no errors; `_site/index.html` is produced.

- [ ] **Step 9: Commit**

```bash
git add .gitignore _quarto.yml index.qmd figures/_metadata.yml figures/example_trajectory.qmd README.md outputs/example_trajectory.pdf outputs/example_trajectory.svg
git commit -m "feat: add Quarto project, gallery, and example figure"
```

---

## Notes for the implementer

- If `uv run quarto render` cannot find Python, ensure you run it under `uv run`
  (this puts the project's `.venv` Python on `PATH` so Quarto's jupyter engine
  uses the locked environment).
- The first `movement` import may be slow; that is expected.
- `PALETTE` hex values and `FIGSIZES` dimensions are sensible defaults — Niko can
  tune them later without touching the architecture.
