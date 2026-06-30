# Seaborn-Style Restyle + Set2 Palette Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restyle `movement_figures` to seaborn's `ticks`/`poster` look with the Barlow poster font and ColorBrewer Set2 as the brand cycle + revised `PALETTE`, and apply it to the existing figures.

**Architecture:** Two tasks. Task 1 rewrites the mplstyle sheets and `style.py`/`__init__.py` (new `SET2`, revised `PALETTE`), adds the `seaborn` dependency, and updates the style tests. Task 2 updates the pupil figure (centroid + per-figure `despine`) and re-renders + re-commits both committed figures, whose outputs change under the new style.

**Tech Stack:** matplotlib mplstyle, seaborn (despine), uv, Quarto, pytest.

## Global Constraints

- Ticks look in `movement-base.mplstyle` (all media), despined top/right; greys `0.15`; ticks out.
- Base `axes.prop_cycle` = Set2; `font.sans-serif` = Arial→DejaVu list.
- Output quality in base: `pdf.fonttype: 42`, `ps.fonttype: 42`, `svg.fonttype: none`, `savefig.dpi: 300`.
- Poster sheet = seaborn `poster` context sizes/widths + `font.sans-serif: Barlow, DejaVu Sans, sans-serif`.
- `SET2` exported tuple = `#66c2a5 #fc8d62 #8da0cb #e78ac3 #a6d854 #ffd92f #e5c494 #b3b3b3`.
- `PALETTE` = `primary #66c2a5, secondary #fc8d62, accent #e7298a, muted #b3b3b3, highlight #f4cae4, ink #666666`.
- Despine is per-figure (`seaborn.despine(fig=fig, trim=True)`), NOT in `save_figure`.
- Centroid marker: `color=PALETTE["highlight"]`, `marker="x"`, `s=220`, `linewidths=4`.
- `manuscript`/`presentation` sheets unchanged; `apply_style` signature unchanged.
- All commands under `uv run`. Committed figure outputs must stay byte-deterministic on re-render.

---

### Task 1: Restyle the package (sheets, palette, deps, tests)

**Files:**
- Modify: `pyproject.toml`
- Rewrite: `src/movement_figures/styles/movement-base.mplstyle`
- Rewrite: `src/movement_figures/styles/movement-poster.mplstyle`
- Modify: `src/movement_figures/style.py`
- Modify: `src/movement_figures/__init__.py`
- Modify: `tests/test_style.py`

**Interfaces:**
- Produces: `SET2: tuple[str, ...]` and a revised `PALETTE: dict[str, str]` exported from `movement_figures`; base color cycle = `SET2`.

- [ ] **Step 1: Add seaborn dependency**

In `pyproject.toml`, add `"seaborn"` to `[project].dependencies` (after `"matplotlib"`):

```toml
dependencies = [
    "movement>=0.17",
    "matplotlib",
    "seaborn",
    "numpy",
    "jupyter",
    "nbformat",
    "nbclient",
]
```

Then run: `uv sync`
Expected: installs seaborn into `.venv`.

- [ ] **Step 2: Rewrite `movement-base.mplstyle`**

Replace the entire file `src/movement_figures/styles/movement-base.mplstyle` with:

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

- [ ] **Step 3: Rewrite `movement-poster.mplstyle`**

Replace the entire file `src/movement_figures/styles/movement-poster.mplstyle` with:

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

- [ ] **Step 4: Add `SET2` and revise `PALETTE` in `style.py`**

In `src/movement_figures/style.py`, replace the existing `PALETTE` assignment block:

```python
# Named colors aligned with movement branding (adjust hex values to taste).
PALETTE: dict[str, str] = {
    "primary": "#2a9d8f",
    "secondary": "#e76f51",
    "accent": "#264653",
    "muted": "#8d99ae",
}
```

with:

```python
# ColorBrewer Set2 — movement's brand categorical palette (matches the base
# axes.prop_cycle in movement-base.mplstyle).
SET2: tuple[str, ...] = (
    "#66c2a5",
    "#fc8d62",
    "#8da0cb",
    "#e78ac3",
    "#a6d854",
    "#ffd92f",
    "#e5c494",
    "#b3b3b3",
)

# Semantic colors drawn from the cohesive Set2 / Dark2 / Pastel2 family.
PALETTE: dict[str, str] = {
    "primary": "#66c2a5",  # Set2 teal
    "secondary": "#fc8d62",  # Set2 orange
    "accent": "#e7298a",  # Dark2 magenta (vivid)
    "muted": "#b3b3b3",  # Set2 grey
    "highlight": "#f4cae4",  # Pastel2 pink (light marks on dark)
    "ink": "#666666",  # Dark2 grey (dark neutral)
}
```

(If the exact comment/spacing of the old block differs, match the file: the goal
is to add the `SET2` tuple and replace the four old `PALETTE` entries with the six
new ones.)

- [ ] **Step 5: Export `SET2` from the package**

In `src/movement_figures/__init__.py`, add `SET2` to the `style` import and to
`__all__`:

```python
"""Shared style and helpers for movement research figures."""

from movement_figures.io import save_figure
from movement_figures.style import (
    AVAILABLE_MEDIA,
    FIGSIZES,
    PALETTE,
    SET2,
    apply_style,
)

__all__ = [
    "AVAILABLE_MEDIA",
    "FIGSIZES",
    "PALETTE",
    "SET2",
    "apply_style",
    "save_figure",
]
```

- [ ] **Step 6: Update the style tests**

In `tests/test_style.py`, update the imports and the poster-fontsize test, and add
two tests. New top of file:

```python
import matplotlib.pyplot as plt
import pytest
from matplotlib.colors import to_hex

from movement_figures import (
    AVAILABLE_MEDIA,
    FIGSIZES,
    PALETTE,
    SET2,
    apply_style,
)
```

Change `test_apply_style_poster_fontsize` to assert `24`:

```python
def test_apply_style_poster_fontsize():
    apply_style("poster")
    assert plt.rcParams["font.size"] == 24
```

Add these two tests:

```python
def test_apply_style_color_cycle_matches_set2():
    apply_style("poster")
    cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    assert [to_hex(c) for c in cycle] == [to_hex(c) for c in SET2]


def test_palette_keys():
    assert set(PALETTE) == {
        "primary",
        "secondary",
        "accent",
        "muted",
        "highlight",
        "ink",
    }
```

- [ ] **Step 7: Run the style tests**

Run: `uv run pytest tests/test_style.py -v`
Expected: all pass (9 tests in this file: 7 prior with the poster one updated, plus
2 new). If `test_apply_style_color_cycle_matches_set2` fails, check the
`axes.prop_cycle` line in `movement-base.mplstyle` matches `SET2` exactly.

- [ ] **Step 8: Format, then run the full suite and ruff**

Run: `uv run ruff format . && uv run pytest -q && uv run ruff check .`
Expected: format applies cleanly; `14 passed`; ruff `All checks passed!`. (Fix any
ruff finding in the changed `.py` files properly; do not silence real findings.)

- [ ] **Step 9: Commit**

```bash
git add pyproject.toml uv.lock src/movement_figures tests/test_style.py
git commit -m "feat: seaborn ticks/poster style, Set2 cycle, revised PALETTE"
```

---

### Task 2: Update the pupil figure and re-render both figures

**Files:**
- Modify: `figures/pupil_tracking_poster.qmd`
- Regenerate (committed): `outputs/pupil_tracking_poster.{pdf,svg}`, `outputs/example_trajectory.{pdf,svg}`

**Interfaces:**
- Consumes: `PALETTE` (with `highlight`), the new base/poster style, and `seaborn` from Task 1.

**Note on "test":** verification = renders succeed, outputs regenerate, re-render is
diff-free, suite stays green. Run each and confirm.

- [ ] **Step 1: Add the seaborn import to the pupil figure**

In `figures/pupil_tracking_poster.qmd`, in the "Imports and style" cell, add
`import seaborn as sns` under the existing `import sleap_io as sio` line:

```python
import matplotlib.pyplot as plt
import seaborn as sns
import sleap_io as sio
```

- [ ] **Step 2: Restyle the centroid marker**

In the "Build the figure" cell, change the centroid `scatter` call from:

```python
ax_frame.scatter(
    centroid0.sel(space="x"),
    centroid0.sel(space="y"),
    marker="x",
    s=160,
    color=PALETTE["accent"],
    label="centroid",
)
```

to:

```python
ax_frame.scatter(
    centroid0.sel(space="x"),
    centroid0.sel(space="y"),
    marker="x",
    s=220,
    linewidths=4,
    color=PALETTE["highlight"],
    label="centroid",
)
```

- [ ] **Step 3: Add the per-figure despine**

In the "Save the figure" cell, add `sns.despine(fig=fig, trim=True)` BEFORE
`fig.tight_layout()`:

```python
sns.despine(fig=fig, trim=True)
fig.tight_layout()
save_figure(fig, "pupil_tracking_poster")
fig
```

- [ ] **Step 4: Render the pupil figure**

Run: `uv run quarto render figures/pupil_tracking_poster.qmd`
Expected: render succeeds; `outputs/pupil_tracking_poster.{pdf,svg}` updated. The
keypoints now use Set2 colors, the centroid is a thick light marker, and the
velocity panel's spines are trimmed.

- [ ] **Step 5: Render the example figure (its output changes under the new base style)**

Run: `uv run quarto render figures/example_trajectory.qmd`
Expected: render succeeds; `outputs/example_trajectory.{pdf,svg}` updated (new
Set2/`PALETTE` colors, greys, embedded fonts).

- [ ] **Step 6: Verify determinism (re-render → no diff)**

Run:
```bash
git add outputs/pupil_tracking_poster.pdf outputs/pupil_tracking_poster.svg outputs/example_trajectory.pdf outputs/example_trajectory.svg
uv run quarto render figures/pupil_tracking_poster.qmd >/dev/null 2>&1
uv run quarto render figures/example_trajectory.qmd >/dev/null 2>&1
git status --porcelain outputs/
```
Expected: the four outputs show staged (`A`/`M`) with NO trailing unstaged
modification — i.e. the second render produced identical bytes.

- [ ] **Step 7: Render the whole project and run the suite**

Run: `uv run quarto render >/dev/null 2>&1 && echo RENDER_OK && uv run pytest -q`
Expected: `RENDER_OK` and `14 passed`.

- [ ] **Step 8: Commit**

```bash
git add figures/pupil_tracking_poster.qmd outputs/pupil_tracking_poster.pdf outputs/pupil_tracking_poster.svg outputs/example_trajectory.pdf outputs/example_trajectory.svg
git commit -m "feat: apply seaborn style + Set2 to figures; trim-despine pupil figure"
```

(Do not stage `draft_pupil_figure.py`, `_site/`, or `_freeze/`.)

---

## Notes for the implementer

- Run everything under `uv run`. Barlow is installed locally
  (`~/Library/Fonts/Barlow-Regular.ttf`); matplotlib finds it by family name.
- Importing seaborn does NOT change rcParams — only `sns.set_theme()` would, and
  we never call it. The mplstyle from `apply_style` governs the look.
- `sns.despine(fig=fig, trim=True)` trims the velocity panel's spines to the
  first/last tick; the tick-less image panel is left alone by `trim`.
- If a render's second pass produces a diff, stop and report it — do not just
  re-commit; it means something non-deterministic slipped in.
