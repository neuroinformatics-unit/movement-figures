"""Matplotlib figures of the bees' metrics, revealed one panel at a time.

Every stage is the same figure with later panels hidden, so the layout does
not shift as panels appear.
"""

from pathlib import Path

import numpy as np
from bees import COLOURS, NAMES, WINDOW, load_clean, metrics
from common import BLUE, use_brand_font_in_plots

OUT = Path(__file__).resolve().parent.parent / "cache" / "bees"
FIGSIZE = (9.6, 5.6)  # inches; sets text size relative to the plots
STAGES = 2  # speed and distance; + head direction


def plot_polar_histogram(da, bin_width_deg=15, ax=None, **kwargs):
    """Polar histogram of angles, from movement's head-direction example."""
    import matplotlib.pyplot as plt

    n_bins = int(360 / bin_width_deg)
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(5, 5), subplot_kw={"projection": "polar"})
    else:
        fig = ax.figure
    da.plot.hist(
        bins=np.linspace(-np.pi, np.pi, n_bins + 1), ax=ax, density=True, **kwargs
    )
    ax.set_theta_direction(-1)  # theta increases in clockwise direction
    ax.set_theta_offset(0)  # set zero at the right
    ax.set_xlabel("")  # remove default x-label from xarray's plot.hist()
    n_xtick_edges = 9
    ax.set_xticks(np.linspace(0, 2 * np.pi, n_xtick_edges)[:-1])
    xticks_in_deg = list(range(0, 180 + 45, 45)) + list(range(0, -180, -45))[-1:0:-1]
    ax.set_xticklabels([str(t) + "\N{DEGREE SIGN}" for t in xticks_in_deg])
    return fig, ax


def render(height_px, force=False):
    """Write stage_1.png and stage_2.png, ``height_px`` tall; return their
    paths."""
    out = OUT / f"{height_px}px"
    dpi = height_px / FIGSIZE[1]
    paths = [out / f"stage_{i}.png" for i in range(1, STAGES + 1)]
    if all(p.exists() for p in paths) and not force:
        return paths

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    use_brand_font_in_plots()

    speed, distance, heading = metrics(load_clean())
    # Time from the start of the clip shown in the video
    speed, distance, heading = (
        da.assign_coords(time=da.time - WINDOW[0]) for da in (speed, distance, heading)
    )

    from cycler import cycler

    # movement's brand colours, shared with the skeletons in the video
    plt.rcParams.update({"font.size": 14, "axes.prop_cycle": cycler(color=COLOURS)})
    out.mkdir(parents=True, exist_ok=True)
    for stage, path in enumerate(paths, start=1):
        fig = plt.figure(figsize=FIGSIZE)
        grid = fig.add_gridspec(
            2, 2, width_ratios=[1.6, 1], left=0.1, right=0.97, bottom=0.12,
            top=0.84, wspace=0.35, hspace=0.45,
        )  # fmt: skip
        ax_speed = fig.add_subplot(grid[0, 0])
        ax_dist = fig.add_subplot(grid[1, 0], sharex=ax_speed)
        ax_polar = [fig.add_subplot(grid[i, 1], projection="polar") for i in range(2)]

        speed.plot.line(x="time", hue="individual", ax=ax_speed)
        ax_speed.set_title("Speed")
        ax_speed.set(xlabel="", ylabel="speed (px/s)")

        distance.plot(ax=ax_dist, color=BLUE)
        ax_dist.set_title("Distance between bees")
        ax_dist.set(xlabel="time (s)", ylabel="distance (px)")

        for i, (ax, name) in enumerate(zip(ax_polar, NAMES, strict=True)):
            plot_polar_histogram(
                heading.sel(individual=name), bin_width_deg=30, ax=ax, color=COLOURS[i]
            )
            # Bars share the speed legend's colours, so no per-bee title
            # (clears xarray's automatic "individual = …" title)
            ax.set_title("")
            ax.set_yticklabels([])
            ax.tick_params(labelsize=13)
        heading_title = fig.text(
            0.83,
            0.9,
            "Head direction",
            ha="center",
            fontsize=plt.rcParams["axes.titlesize"],
        )

        hidden = [*ax_polar, heading_title] * (stage < 2)
        for ax in hidden:
            ax.set_visible(False)
        fig.savefig(path, dpi=dpi, transparent=True)
        plt.close(fig)
    return paths


if __name__ == "__main__":
    print(render(height_px=742, force=True))
