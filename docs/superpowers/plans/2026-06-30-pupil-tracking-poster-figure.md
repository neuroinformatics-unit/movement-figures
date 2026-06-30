# Pupil-Tracking Poster Figure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a single two-panel poster figure (`figures/pupil_tracking_poster.qmd`) showing tracked eye keypoints on an example frame and the pupil centroid's x-velocity over time, for the `black` rotating-mouse dataset.

**Architecture:** One flat Quarto figure document following the pattern of `figures/example_trajectory.qmd`: a short narrative plus one `{python}` cell that loads the dataset (with video), draws two side-by-side panels, applies the poster style, and exports vector files via `save_figure`. No package code changes.

**Tech Stack:** Quarto (jupyter engine), movement (`sample_data`, `kinematics.compute_velocity`), sleap_io, matplotlib, the `movement_figures` helpers.

## Global Constraints

- File: `figures/pupil_tracking_poster.qmd` (flat, one figure per qmd).
- Medium: `apply_style("poster")`; figure size `FIGSIZES["poster"]["double"]` (16×9).
- Dataset: `black` only — `DLC_rotating-mouse_eye-tracking_stim-black.predictions.h5`, fetched `with_video=True`.
- Panel 1: `video[0]` frame + the 4 keypoints at `position.isel(time=0)` + pupil-centroid marker (`x`, `PALETTE["accent"]`, label "centroid").
- Panel 2: x-velocity of the **normalized** pupil centroid (positions minus eye midpoint), time window `slice(10, 25)` s.
- Export: end the cell with `save_figure(fig, "pupil_tracking_poster")` then a bare `fig`.
- Commit the vector outputs (`outputs/pupil_tracking_poster.{pdf,svg}`); they must be byte-stable across re-renders.
- Do NOT port the draft's other sections (uniform dataset, pupil diameter, blink distance, filtering, normalized-position line plots, seaborn). `draft_pupil_figure.py` is reference-only and must NOT be staged/committed.
- All commands under `uv run`.

---

### Task 1: Pupil-tracking poster figure

**Files:**
- Create: `figures/pupil_tracking_poster.qmd`
- Create (generated, committed): `outputs/pupil_tracking_poster.pdf`, `outputs/pupil_tracking_poster.svg`

**Interfaces:**
- Consumes: `apply_style`, `save_figure`, `FIGSIZES`, `PALETTE` from `movement_figures`; `movement.sample_data.fetch_dataset`, `movement.kinematics.compute_velocity`, `sleap_io.load_video`.
- Produces: a figure document that renders standalone and as part of the gallery.

**Note on "test":** there is no unit test for a figure. The verification commands (render succeeds, both output files exist and are non-empty, a second render produces no `outputs/` diff, suite still green) ARE the acceptance criteria — run each and confirm the stated result.

- [ ] **Step 1: Create `figures/pupil_tracking_poster.qmd`**

Write exactly this file:

````markdown
---
title: "Pupil tracking (poster)"
---

A two-panel poster figure for the `black` (dark surround) rotating-mouse
eye-tracking dataset: the four tracked keypoints (plus the pupil centroid) on an
example video frame, and the pupil centroid's horizontal velocity over time.

```{python}
import matplotlib.pyplot as plt
import sleap_io as sio

from movement import sample_data
from movement.kinematics import compute_velocity

from movement_figures import FIGSIZES, PALETTE, apply_style, save_figure

apply_style("poster")

# Load the black (dark surround) eye-tracking dataset together with its video.
ds = sample_data.fetch_dataset(
    "DLC_rotating-mouse_eye-tracking_stim-black.predictions.h5",
    with_video=True,
)
frame0 = sio.load_video(ds.video_path)[0]

fig, (ax_frame, ax_vel) = plt.subplots(
    1, 2, figsize=FIGSIZES["poster"]["double"]
)

# Panel 1: example frame with the tracked keypoints and the pupil centroid.
pos0 = ds.position.isel(time=0).squeeze()
ax_frame.imshow(frame0, cmap="gray")
for keypoint in ds.keypoints.values:
    p = pos0.sel(keypoints=keypoint)
    ax_frame.scatter(p.sel(space="x"), p.sel(space="y"), s=120, label=keypoint)
centroid0 = pos0.sel(keypoints=["pupil-L", "pupil-R"]).mean("keypoints")
ax_frame.scatter(
    centroid0.sel(space="x"),
    centroid0.sel(space="y"),
    marker="x",
    s=160,
    color=PALETTE["accent"],
    label="centroid",
)
ax_frame.invert_yaxis()  # the dataset was captured flipped
ax_frame.set_xticks([])
ax_frame.set_yticks([])
ax_frame.set_title("Tracked keypoints")
ax_frame.legend(loc="upper right")

# Panel 2: x-velocity of the normalized pupil centroid over time.
eye_mid = ds.position.sel(keypoints=["eye-L", "eye-R"]).mean("keypoints")
pos_norm = ds.position - eye_mid
pupil_c = pos_norm.sel(keypoints=["pupil-L", "pupil-R"]).mean("keypoints")
velocity = compute_velocity(pupil_c)
vx = velocity.sel(space="x").squeeze().sel(time=slice(10, 25))
vx.plot.line(ax=ax_vel)
ax_vel.set_title("Pupil centroid x-velocity")
ax_vel.set_xlabel("time (s)")
ax_vel.set_ylabel("velocity (px/s)")

fig.tight_layout()
save_figure(fig, "pupil_tracking_poster")
fig
```
````

- [ ] **Step 2: Render the figure**

Run: `uv run quarto render figures/pupil_tracking_poster.qmd`
Expected: render completes with no error. First run downloads the dataset +
video via pooch (may take a while). If the render fails, debug it (it is a real
failure). If a movement/sleap_io API call genuinely does not behave as written
(e.g. a keypoint name or dimension differs), report the exact error rather than
guessing — but the names above match the draft (`pupil-L`, `pupil-R`, `eye-L`,
`eye-R`; dims `time`/`keypoints`/`space`/`individuals`).

- [ ] **Step 3: Verify both output files exist and are non-empty**

Run: `ls -l outputs/pupil_tracking_poster.pdf outputs/pupil_tracking_poster.svg`
Expected: both files listed with non-zero size.

- [ ] **Step 4: Verify the outputs are deterministic (no diff on re-render)**

Run: `uv run quarto render figures/pupil_tracking_poster.qmd && git status --porcelain outputs/`
Expected: after the first render's outputs are staged (next step) this would be
empty; for now confirm the render re-runs cleanly. (The shared `save_figure`
suppresses timestamps and pins the SVG hash salt, so repeated renders of the
same frame produce identical bytes.)

- [ ] **Step 5: Render the whole project (gallery includes the new figure)**

Run: `uv run quarto render`
Expected: full build succeeds; the new figure appears as a card in the gallery
(`_site/index.html`).

- [ ] **Step 6: Verify the test suite is still green**

Run: `uv run pytest -q`
Expected: `12 passed` (no package code changed).

- [ ] **Step 7: Commit**

Stage ONLY the figure and its outputs — do not stage `draft_pupil_figure.py` or
anything under `_site/`/`.quarto/`:

```bash
git add figures/pupil_tracking_poster.qmd outputs/pupil_tracking_poster.pdf outputs/pupil_tracking_poster.svg
git commit -m "feat: add pupil-tracking poster figure"
```

If the pre-commit hooks modify the `.qmd` (e.g. add a trailing newline), re-stage
it and commit again. Confirm `git status` shows a clean tree afterward (the
untracked `draft_pupil_figure.py` may remain — that is expected and intentional).

---

## Notes for the implementer

- Run everything under `uv run` so Quarto's jupyter engine uses the locked `.venv`.
- `ds.position` dims are `time`, `individuals`, `keypoints`, `space`; `.squeeze()`
  drops the singleton `individuals` axis. `sel(space="x")`/`sel(space="y")` pick
  the coordinate components.
- `ds.video_path` is the local cached path to the downloaded video; `sleap_io`
  reads frames from it (`sio.load_video(path)[0]` is the first frame as an array).
- Do not touch `figures/*.qmd` other than the new file, the package, or the tests.
