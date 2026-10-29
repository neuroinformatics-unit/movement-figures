"""Matplotlib figures made with movement's own plotting functions, and the
matching EPM video clip."""

import json
from pathlib import Path

import numpy as np
from clean_viz_data import EPM, MAZE_CROP, OCCUPANCY_BIN, WINDOW, clean_epm
from common import GREEN, ORANGE

OUT = Path(__file__).resolve().parent.parent / "cache" / "clean_viz"
FIGSIZE = (11, 6)  # inches; sets text size relative to the plots
VIDEO_HEIGHT, VIDEO_WIDTH = 1028, 1300
VIDEO_FPS = 30
# Recorded frames per clip frame; at 3x playback, the clip plays at 30 fps
CLIP_STEP = 3
# Its raw track is the noisiest, so cleaning shows best
CLEANED_KEYPOINT, CLEANED_LABEL = "tail_end", "Tail tip"
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


def video_clip(height_px):
    """Every ``CLIP_STEP``-th frame of the trajectory window, cropped to the
    maze and ``height_px`` tall, with the raw poses in video pixels
    ([time, keypoint, space]).
    """
    path = OUT / f"clip_{height_px}px.npz"
    if not path.exists():
        ds, _, start, n = _load()
        x0, x1 = MAZE_CROP
        width = round((x1 - x0) * height_px / VIDEO_HEIGHT / 2) * 2
        clip = _video_frames(
            f"select=between(n\\,{start}\\,{start + n - 1})"
            f"*not(mod(n-{start}\\,{CLIP_STEP})),"
            f"crop={x1 - x0}:{VIDEO_HEIGHT}:{x0}:0,scale={width}:{height_px}",
            height_px,
            width,
        )
        poses = ds.position.isel(time=slice(start, start + n, CLIP_STEP))
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
    """Write the cleaning plot's layers (axes, raw, cleaned), trajectory.png
    and trajectory + occupancy.png, ``height_px`` tall, all laid out alike.

    Returns their paths and, as figure fractions (left, bottom, width,
    height), the two maze axes' boxes, so the clip can be laid over the
    first, and the cleaning plot's axes, so its lines can be revealed in
    time.
    """
    out = OUT / f"{height_px}px"
    dpi = height_px / FIGSIZE[1]
    paths = [out / f"cleaning_{layer}.png" for layer in ("axes", "raw", "cleaned")] + [
        out / "trajectory.png",
        out / "occupancy.png",
    ]
    boxes_path = out / "boxes.json"
    if all(p.exists() for p in paths + [boxes_path]) and not force:
        return paths, json.loads(boxes_path.read_text())

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

    for path, show_occupancy in zip(paths[3:], (False, True), strict=True):
        fig = draw(show_occupancy)
        fig.savefig(path, dpi=dpi, transparent=True)
        # After drawing, so the boxes reflect the colourbar and aspect
        boxes = [list(ax.get_position().bounds) for ax in fig.axes[:2]]
        plt.close(fig)

    # Raw vs cleaned position of one keypoint, in the occupancy plot's slot
    # (right of the clip, which plays in the trajectory plot's maze), as
    # three layers: the axes, then each line with its legend entry. Raw goes
    # on top, so its outliers stand out against the cleaned line
    (left, _, w, _), (_, bottom, _, h) = boxes
    left += w + 0.1  # room for the tick labels
    bottom += 0.09  # room for the time axis
    height = (h - 0.09 - 0.04) / 2
    right = 0.9  # leaves room for the last tick label within the frame
    series = {
        "raw": ds.position.isel(time=slice(start, start + n)),
        "cleaned": window,
    }
    series = {k: v.sel(keypoint=CLEANED_KEYPOINT) for k, v in series.items()}
    styles = {"raw": dict(color=ORANGE, lw=1.2), "cleaned": dict(color=GREEN, lw=4)}
    for path, layer in zip(paths[:3], ("axes", "raw", "cleaned"), strict=True):
        fig = plt.figure(figsize=FIGSIZE)
        lower = fig.add_axes([left, bottom, right - left, height])
        upper = fig.add_axes([left, bottom + height + 0.04, right - left, height])
        upper.sharex(lower)
        handles = []
        for ax, axis in zip((upper, lower), ("x", "y"), strict=True):
            # Every layer plots both lines, so all share the same limits
            for name in ("raw", "cleaned"):
                (line,) = (
                    series[name]
                    .sel(space=axis)
                    .plot.line(x="time", ax=ax, label=name, **styles[name])
                )
                line.set_visible(name == layer)
                if ax is upper:
                    handles.append(line)
            ax.set(title="", xlabel="", ylabel=axis)
        if layer == "axes":
            upper.tick_params(labelbottom=False)
            upper.set_title(CLEANED_LABEL, loc="left")
            lower.set_xlabel("Time (s)")
        else:
            for ax in (upper, lower):
                ax.axis("off")
            # Both entries, so each keeps its place; only this layer's shows
            legend = upper.legend(
                handles=handles,
                loc="lower right",
                bbox_to_anchor=(1, 1),
                ncols=2,
                frameon=False,
                borderaxespad=0,
            )
            for handle, text in zip(legend.legend_handles, legend.texts, strict=True):
                visible = text.get_text() == layer
                handle.set_visible(visible)
                text.set_visible(visible)
        lower.set_xlim(*WINDOW)
        fig.savefig(path, dpi=dpi, transparent=True)
        plt.close(fig)
    boxes.append([left, bottom, right - left, 2 * height + 0.04])

    boxes_path.write_text(json.dumps(boxes))
    return paths, boxes


if __name__ == "__main__":
    print(render(height_px=729, force=True))
