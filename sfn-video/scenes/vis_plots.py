"""Matplotlib figures made with movement's own plotting functions.

The trajectory is revealed by re-plotting a growing time slice, so every
video frame is a genuine output of ``plot_centroid_trajectory``.
"""

from pathlib import Path

import numpy as np
from analysis_data import EPM, MAZE_CROP, OCCUPANCY_BIN, TRAJECTORY_SECONDS, _clean

OUT = Path(__file__).resolve().parent.parent / "cache" / "visualise"
N_STEPS = 60  # trajectory reveal frames
FIGSIZE = (11, 6)  # inches; sets text size relative to the plots
VIDEO_SOURCE = "DLC_single-mouse_EPM.predictions.h5"
VIDEO_HEIGHT, VIDEO_WIDTH = 1028, 1300


def _layout():
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.size": 18})
    # A fixed layout (not constrained), so colourbars take the same space in
    # every frame whether or not they are shown
    fig, (ax_traj, ax_occ) = plt.subplots(1, 2, figsize=FIGSIZE)
    fig.subplots_adjust(left=0.02, right=0.93, bottom=0.02, top=0.93, wspace=0.3)
    return fig, ax_traj, ax_occ


def _maze_limits(ax, frame):
    ax.set_xlim(*MAZE_CROP)
    ax.set_ylim(frame.shape[0], 0)


def _maze(ax, frame):
    ax.imshow(frame, cmap="gray")
    _maze_limits(ax, frame)


def _video_frame(index):
    """Greyscale frame of the EPM video.

    The SLEAP EPM sample ships without video, but tracks the same recording as
    the DLC EPM sample, whose video we borrow.
    """
    import subprocess

    from movement import sample_data

    video = sample_data.fetch_dataset(VIDEO_SOURCE, with_video=True).attrs["video_path"]
    raw = subprocess.run(
        [
            "ffmpeg",
            "-loglevel",
            "error",
            "-i",
            str(video),
            "-vf",
            f"select=eq(n\\,{index})",
            "-frames:v",
            "1",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "gray",
            "-",
        ],  # fmt: skip
        capture_output=True,
        check=True,
    ).stdout
    return np.frombuffer(raw, np.uint8).reshape(VIDEO_HEIGHT, VIDEO_WIDTH)


def render(height_px, force=False):
    """Write trajectory_XX.png reveal frames and occupancy.png, ``height_px`` tall."""
    out = OUT / f"{height_px}px"
    dpi = height_px / FIGSIZE[1]
    final = out / "occupancy.png"
    if final.exists() and not force:
        return sorted(out.glob("trajectory_*.png")), final

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from movement import sample_data
    from movement.plots import plot_centroid_trajectory, plot_occupancy

    ds = sample_data.fetch_dataset(EPM).squeeze("individual")
    position = _clean(ds.position, ds.confidence)

    # The window that covers the most of the maze
    n = int(TRAJECTORY_SECONDS * ds.attrs["fps"])
    centroid = position.mean("keypoint").transpose("time", "space").values
    starts = range(0, len(centroid) - n, n // 4)
    start = max(starts, key=lambda s: np.nanstd(centroid[s : s + n], axis=0).sum())
    window = position.isel(time=slice(start, start + n))
    t0, t1 = float(window.time[0]), float(window.time[-1])
    # Background: the video frame where the trajectory ends
    frame = _video_frame(start + n - 1)

    height, width = frame.shape
    bins = [
        np.arange(0, width + OCCUPANCY_BIN, OCCUPANCY_BIN),
        np.arange(0, height + OCCUPANCY_BIN, OCCUPANCY_BIN),
    ]

    def draw(n_shown, show_occupancy):
        fig, ax_traj, ax_occ = _layout()
        _maze(ax_traj, frame)
        _maze(ax_occ, frame)
        plot_centroid_trajectory(
            window.isel(time=slice(0, n_shown)), ax=ax_traj, vmin=t0, vmax=t1
        )
        before = set(fig.axes)
        plot_occupancy(position, ax=ax_occ, bins=bins, cmin=10, norm="log", alpha=0.8)
        if not show_occupancy:
            # Hide the whole subplot, keeping its space, so the layout
            # doesn't shift when it appears
            for ax in {ax_occ} | (set(fig.axes) - before):
                ax.set_visible(False)
        _maze_limits(ax_occ, frame)
        ax_occ.set_title("Occupancy")
        for ax in (ax_traj, ax_occ):
            ax.axis("off")  # pixel coordinates mean nothing to viewers
        return fig

    out.mkdir(parents=True, exist_ok=True)
    paths = []
    for step in range(1, N_STEPS + 1):
        fig = draw(step * n // N_STEPS, show_occupancy=False)
        path = out / f"trajectory_{step:02d}.png"
        fig.savefig(path, dpi=dpi, transparent=True)
        plt.close(fig)
        paths.append(path)

    fig = draw(n, show_occupancy=True)
    fig.savefig(final, dpi=dpi, transparent=True)
    plt.close(fig)
    return paths, final


if __name__ == "__main__":
    paths, final = render(height_px=729, force=True)
    print(len(paths), final)
