"""Matplotlib figures of the bees' metrics, revealed one panel at a time.

Every stage is the same figure with later panels hidden, so the layout does
not shift as panels appear.
"""

from pathlib import Path

from bees import COLOURS, NAMES, WINDOW, load_clean, metrics
from common import BLUE, use_brand_font_in_plots

from movement_figures import plot_polar_histogram

OUT = Path(__file__).resolve().parent.parent / "cache" / "bees"
FIGSIZE = (9.6, 5.6)  # inches; sets text size relative to the plots
STAGES = 2  # speed and distance; + head direction


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
        ax_speed.set(xlabel="", ylabel="speed (cm/s)")

        distance.plot(ax=ax_dist, color=BLUE)
        ax_dist.set_title("Distance between bees")
        ax_dist.set(xlabel="time (s)", ylabel="distance (cm)")

        for i, (ax, name) in enumerate(zip(ax_polar, NAMES, strict=True)):
            plot_polar_histogram(
                heading.sel(individual=name),
                ax=ax,
                bin_width_deg=30,
                color=COLOURS[i],
                edgecolor="none",
            )
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
