"""Two interacting bees: tracks, video frames and movement-computed metrics.

Source: a SLEAP-tracked recording (in ``inputs/``, not committed).
"""

import numpy as np
from common import GREEN, INPUTS, ORANGE, ROOT

SLP = INPUTS / "bees@21000-23000.slp"
VIDEO = INPUTS / "bees@21000-23000.mp4"
CACHE = ROOT / "cache" / "bees"

# Recording rate, per SLEAP's datasets page; the clip's mp4 header says 25 fps
FPS = 100
WINDOW = (12.25, 14.25)  # s; one bee walks over, they meet and stay side by side
PX_PER_CM = 140  # image scale (14 px/mm), per SLEAP's datasets page
ARENA = (240, 0, 1536)  # x0, y0, size (px): a square around the arena
CROP_SIZE = 720  # px; cropped frames are resized to this square
NAMES = ["bee 1", "bee 2"]
COLOURS = [GREEN, ORANGE]  # movement brand colours, one per bee
LEFT, RIGHT = "Lant1", "Rant1"  # antenna bases: a left/right pair on the head
VIDEO_HEIGHT, VIDEO_WIDTH = 1536, 2048


def skeleton_edges():
    import sleap_io as sio

    skeleton = sio.load_slp(str(SLP)).skeletons[0]
    return [(e.source.name, e.destination.name) for e in skeleton.edges]


def load_clean():
    """Cleaned poses for the window, with individuals named ``NAMES``."""
    from movement.filtering import (
        interpolate_over_time,
        rolling_filter,
        savgol_filter,
    )
    from movement.io import load_poses

    ds = load_poses.from_sleap_file(SLP, fps=FPS)
    ds = ds.assign_coords(individual=NAMES).sel(time=slice(*WINDOW))
    # Tracks carry no confidence scores, so no confidence filter
    position = rolling_filter(ds.position, window=7, statistic="median", min_periods=2)
    # Bridges the ~0.2 s occlusion when the bees overlap
    position = interpolate_over_time(position, max_gap=25)
    # SciPy >= 1.17 rejects NaNs in edge windows with the default mode
    return savgol_filter(position, window=15, polyorder=2, mode="nearest")


def metrics(position):
    """Speed (cm/s), inter-bee distance (cm) and head direction, all from
    movement."""
    from movement.kinematics import (
        compute_forward_vector_angle,
        compute_pairwise_distances,
        compute_speed,
    )
    from movement.transforms import scale

    thorax = scale(position.sel(keypoint="thor"), 1 / PX_PER_CM, space_unit="cm")
    speed = compute_speed(thorax)
    distance = compute_pairwise_distances(
        thorax, dim="individual", pairs={NAMES[0]: NAMES[1]}
    )
    heading = compute_forward_vector_angle(
        position, left_keypoint=LEFT, right_keypoint=RIGHT
    )
    return speed, distance, heading


def video_frames(box=ARENA):
    """Cropped greyscale frames of the window, one per recorded frame."""
    path = CACHE / "frames.npy"
    if not path.exists():
        import subprocess

        x0, y0, size = box
        first, last = (int(t * FPS) for t in WINDOW)
        raw = subprocess.run(
            [
                "ffmpeg",
                "-loglevel",
                "error",
                "-i",
                str(VIDEO),
                "-vf",
                f"select=between(n\\,{first}\\,{last}),"
                f"crop={size}:{size}:{x0}:{y0},scale={CROP_SIZE}:{CROP_SIZE}",
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
        CACHE.mkdir(parents=True, exist_ok=True)
        np.save(path, np.frombuffer(raw, np.uint8).reshape(-1, CROP_SIZE, CROP_SIZE))
    return np.load(path)
