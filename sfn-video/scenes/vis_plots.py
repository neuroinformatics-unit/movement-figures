"""Matplotlib figures made with movement's own plotting functions, and the
matching EPM video clip."""

from pathlib import Path

import numpy as np
from analysis_data import EPM, MAZE_CROP, OCCUPANCY_BIN, WINDOW, clean_epm
from common import GREEN, ORANGE

OUT = Path(__file__).resolve().parent.parent / "cache" / "visualise"
FIGSIZE = (11, 6)  # inches; sets text size relative to the plots
VIDEO_HEIGHT, VIDEO_WIDTH = 1028, 1300
VIDEO_FPS = 30
CLIP_STEP = 4  # recorded frames per thumbnail frame
CLIP_HEIGHT = 400  # px
# Narrower, as the constrained layout leaves no margin to the right
CLEANING_FIGSIZE = (10, 6)
CLEANED_KEYPOINT = "snout"  # clear outliers in the window, as on the poster
SKELETON = [
    ("snout", "left_ear"),
    ("snout", "right_ear"),
    ("left_ear", "centre"),
    ("right_ear", "centre"),
    ("centre", "lateral_left"),
    ("centre", "lateral_right"),
    ("lateral_left", "tailbase"),
    ("lateral_right", "tailbase"),
    ("tailbase", "tail_end"),
]
# As on the poster: the noisier snout, laterals and tail end are left out
CENTROID_KEYPOINTS = ["centre", "tailbase", "left_ear", "right_ear"]


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


def _video_frames(vf, height, width):
    """Greyscale frames of the EPM video, through the ffmpeg filter ``vf``."""
    import subprocess

    from movement import sample_data

    video = sample_data.fetch_dataset(EPM, with_video=True).attrs["video_path"]
    raw = subprocess.run(
        [
            "ffmpeg",
            "-loglevel",
            "error",
            "-i",
            str(video),
            "-vf",
            vf,
            "-vsync",
            "0",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "gray",
            "-",
        ],  # fmt: skip
        capture_output=True,
        check=True,
    ).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, height, width)


def _video_frame(index):
    return _video_frames(f"select=eq(n\\,{index})", VIDEO_HEIGHT, VIDEO_WIDTH)[0]


def _load():
    """Raw EPM dataset, cleaned poses, and the start and length (frames) of
    the window shown."""
    from movement import sample_data

    ds = sample_data.fetch_dataset(EPM).squeeze("individual")
    position = clean_epm(ds.position, ds.confidence)
    start, n = (int(t * ds.attrs["fps"]) for t in (WINDOW[0], WINDOW[1] - WINDOW[0]))
    return ds, position, start, n


def video_clip():
    """Every ``CLIP_STEP``-th frame of the trajectory window, cropped to the
    maze, with the cleaned poses in video pixels ([time, keypoint, space]).
    """
    path = OUT / "clip.npz"
    if not path.exists():
        _, position, start, n = _load()
        step = CLIP_STEP
        x0, x1 = MAZE_CROP
        width = round((x1 - x0) * CLIP_HEIGHT / VIDEO_HEIGHT / 2) * 2
        clip = _video_frames(
            f"select=between(n\\,{start}\\,{start + n - 1})"
            f"*not(mod(n-{start}\\,{step})),"
            f"crop={x1 - x0}:{VIDEO_HEIGHT}:{x0}:0,scale={width}:{CLIP_HEIGHT}",
            CLIP_HEIGHT,
            width,
        )
        poses = position.isel(time=slice(start, start + n, step))
        poses = poses.transpose("time", "keypoint", "space")
        OUT.mkdir(parents=True, exist_ok=True)
        np.savez(
            path,
            frames=clip,
            poses=poses.values,
            keypoints=poses.keypoint.values.astype(str),
        )
    data = np.load(path)
    return data["frames"], data["poses"], list(data["keypoints"])


def render(height_px, force=False):
    """Write cleaning.png, trajectory.png and trajectory + occupancy.png,
    ``height_px`` tall."""
    out = OUT / f"{height_px}px"
    dpi = height_px / FIGSIZE[1]
    paths = [out / "cleaning.png", out / "trajectory.png", out / "occupancy.png"]
    if all(p.exists() for p in paths) and not force:
        return paths

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from movement.plots import plot_centroid_trajectory, plot_occupancy

    ds, position, start, n = _load()
    window = position.isel(time=slice(start, start + n))
    # Background: the video frame where the trajectory ends
    frame = _video_frame(start + n - 1)

    height, width = frame.shape
    bins = [
        np.arange(0, width + OCCUPANCY_BIN, OCCUPANCY_BIN),
        np.arange(0, height + OCCUPANCY_BIN, OCCUPANCY_BIN),
    ]

    def draw(show_occupancy):
        fig, ax_traj, ax_occ = _layout()
        _maze(ax_traj, frame)
        _maze(ax_occ, frame)
        plot_centroid_trajectory(window, keypoints=CENTROID_KEYPOINTS, ax=ax_traj)
        ax_traj.set_title("Centroid trajectory")
        before = set(fig.axes)
        plot_occupancy(
            position, ax=ax_occ, bins=bins, cmin=10, norm="log", alpha=0.8, cmap="turbo"
        )
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

    # Raw vs cleaned position of one keypoint; raw on top, so its outliers
    # stand out against the cleaned line
    plt.rcParams.update({"font.size": 18})
    fig, axes = plt.subplots(
        2, 1, figsize=CLEANING_FIGSIZE, sharex=True, layout="constrained"
    )
    raw = ds.position.isel(time=slice(start, start + n)).sel(keypoint=CLEANED_KEYPOINT)
    clean = window.sel(keypoint=CLEANED_KEYPOINT)
    for ax, axis in zip(axes, ("x", "y")):
        clean.sel(space=axis).plot.line(
            x="time", ax=ax, color=GREEN, lw=4, label="clean"
        )
        raw.sel(space=axis).plot.line(
            x="time", ax=ax, color=ORANGE, lw=1.2, label="raw"
        )
        ax.set(title="", xlabel="", ylabel=f"{axis} (px)")
    axes[0].set_title(f"{CLEANED_KEYPOINT.replace('_', ' ').capitalize()} position")
    handles, labels = axes[0].get_legend_handles_labels()
    axes[0].legend(handles[::-1], labels[::-1], loc="upper right", ncols=2)
    axes[1].set_xlabel("Time (s)")
    fig.savefig(paths[0], dpi=dpi, transparent=True)
    plt.close(fig)

    for path, show_occupancy in zip(paths[1:], (False, True)):
        fig = draw(show_occupancy)
        fig.savefig(path, dpi=dpi, transparent=True)
        plt.close(fig)
    return paths


if __name__ == "__main__":
    print(render(height_px=729, force=True))
