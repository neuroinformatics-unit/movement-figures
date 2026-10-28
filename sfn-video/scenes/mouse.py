"""Side-view mouse skeletons from the DBTravelator 2D sample dataset.

The dataset holds a single mouse; three "individuals" are faked by replaying
the same track with different gait phases, so the herd matches the
three-slab data cube schematic.
"""

from pathlib import Path

import numpy as np
from common import BLUE, GREEN, ORANGE

CACHE = Path(__file__).resolve().parent.parent / "cache" / "dbtravelator.npz"
FIRST, LAST = 195, 350  # all kept keypoints have confidence > 0.8 here

BODY = [
    "Nose", "EarL", "Back1", "Back3", "Back6", "Back9", "Back12",
    "Tail1", "Tail4", "Tail8", "Tail12",
]  # fmt: skip
LIMBS = {
    f"{part}{side}": [f"{part}{joint}{side}" for joint in ("Knee", "Ankle", "Toe")]
    for part in ("Forepaw", "Hindpaw")
    for side in ("L", "R")
}
KEYPOINTS = BODY + [k for chain in LIMBS.values() for k in chain]

EDGES = [("Nose", "Back1"), ("EarL", "Back1")]
EDGES += list(zip(BODY[2:-1], BODY[3:], strict=True))
for name, (knee, ankle, toe) in LIMBS.items():
    hip = "Back3" if name.startswith("Fore") else "Back9"
    EDGES += [(hip, knee), (knee, ankle), (ankle, toe)]

# (colour, frame offset, horizontal stagger in px), top lane first.
# The first is the real, unshifted recording, so it lines up with the video.
INDIVIDUALS = [(GREEN, 0, 0), (BLUE, 22, -40), (ORANGE, 44, 10)]
MAX_OFFSET = max(offset for _, offset, _ in INDIVIDUALS)

VIDEO = Path.home() / ".movement/data/videos/single-mouse_DBTravelator_video.avi"
VIDEO_CACHE = CACHE.with_name("dbtravelator_frames.npy")
VIDEO_HEIGHT, VIDEO_WIDTH = 230, 1920

PIX_CY = 142  # vertical pixel coordinate mapped to a lane's centre
FAR_SIDE_OPACITY = 0.4  # left limbs face away from the camera


def _far_side(keypoint):
    return keypoint not in BODY and keypoint.endswith("L")


def load():
    """Return (positions[time, keypoint, xy], camera_x[time]) in pixels."""
    if not CACHE.exists():
        from movement import sample_data
        from movement.filtering import (
            filter_by_confidence,
            interpolate_over_time,
            rolling_filter,
        )

        ds = sample_data.fetch_dataset(
            "DLC_single-mouse_DBTravelator_2D.predictions.h5"
        )
        # Same cleaning as the movement "scale" example
        position = filter_by_confidence(ds.position, ds.confidence, threshold=0.9)
        position = interpolate_over_time(position, max_gap=40)
        position = rolling_filter(position, window=6, min_periods=2, statistic="median")
        pos = (
            position.squeeze("individual")
            .sel(keypoint=KEYPOINTS)
            .isel(time=slice(FIRST, LAST + 1))
            .transpose("time", "keypoint", "space")
            .values
        )
        CACHE.parent.mkdir(exist_ok=True)
        np.savez(CACHE, pos=pos)
    pos = np.load(CACHE)["pos"]
    # Constant-speed camera that follows the mouse along the travelator
    frames = np.arange(len(pos))
    back = pos[:, KEYPOINTS.index("Back6"), 0]
    camera_x = np.polyval(np.polyfit(frames, back, 1), frames)
    return pos, camera_x


def load_video():
    """Greyscale video frames aligned with ``load()``, as [time, y, x]."""
    if not VIDEO_CACHE.exists():
        import subprocess

        raw = subprocess.run(
            [
                "ffmpeg",
                "-loglevel",
                "error",
                "-i",
                str(VIDEO),
                "-vf",
                f"select=between(n\\,{FIRST}\\,{LAST})",
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
        frames = np.frombuffer(raw, np.uint8).reshape(-1, VIDEO_HEIGHT, VIDEO_WIDTH)
        np.save(VIDEO_CACHE, frames)
    return np.load(VIDEO_CACHE)


class Herd:
    """Walking skeletons in stacked lanes, driven by value trackers.

    ``frame`` scrubs through the (interpolated) recording, ``scale`` maps
    pixels to scene units, ``cx``/``cy`` place the top lane and ``spacing``
    sets the distance between lanes. Each lane has its own ``dots`` and
    ``edges`` opacity, so individuals can be revealed one at a time, and
    ``follow`` switches between a camera that tracks the mice and fixed ground.
    """

    def __init__(self, scale, centre, spacing):
        from manim import ValueTracker

        self.pos, self.camera_x = load()
        self.n_frames = len(self.pos) - MAX_OFFSET
        self.frame = ValueTracker(0)
        self.scale = ValueTracker(scale)
        self.cx = ValueTracker(centre[0])
        self.cy = ValueTracker(centre[1])
        self.spacing = ValueTracker(spacing)
        self.dots = [ValueTracker(0) for _ in INDIVIDUALS]
        self.edges = [ValueTracker(0) for _ in INDIVIDUALS]
        self.video = ValueTracker(0)
        self.follow = ValueTracker(1)
        self._frames = None

    def _at(self, f):
        i = min(int(np.floor(f)), len(self.pos) - 2)
        w = f - i
        p = (1 - w) * self.pos[i] + w * self.pos[i + 1]
        c = (1 - w) * self.camera_x[i] + w * self.camera_x[i + 1]
        return p, c

    def _to_scene(self, lane, px, py, cam):
        s = self.scale.get_value()
        _, offset, stagger = INDIVIDUALS[lane]
        # follow=1: camera tracks the mouse; follow=0: fixed ground, with
        # each mouse starting at cx so they run across the screen together
        follow = self.follow.get_value()
        ref = follow * cam + (1 - follow) * self.camera_x[offset]
        x = self.cx.get_value() + s * (px - ref + stagger)
        y = self.cy.get_value() - lane * self.spacing.get_value() - s * (py - PIX_CY)
        return np.stack([x, y, np.zeros_like(x)], axis=-1)

    def _lane_frame(self, lane, f):
        f = self.frame.get_value() if f is None else f
        return self._at(f + INDIVIDUALS[lane][1])

    def keypoints(self, lane, f=None):
        p, cam = self._lane_frame(lane, f)
        return self._to_scene(lane, p[:, 0], p[:, 1], cam)

    def colour(self, lane):
        return INDIVIDUALS[lane][0]

    def skeletons(self):
        from manim import Dot, Line, VGroup

        herd = VGroup()
        for lane in range(len(INDIVIDUALS)):
            colour = self.colour(lane)
            dot_op = self.dots[lane].get_value()
            edge_op = self.edges[lane].get_value()
            if dot_op == 0 and edge_op == 0:
                continue
            pts = dict(zip(KEYPOINTS, self.keypoints(lane), strict=True))
            edges = VGroup(
                *[
                    Line(
                        pts[a],
                        pts[b],
                        color=colour,
                        stroke_width=6,
                        stroke_opacity=edge_op
                        * (FAR_SIDE_OPACITY if _far_side(b) else 1),
                    )
                    for a, b in sorted(EDGES, key=lambda e: not _far_side(e[1]))
                ]
            )
            dots = VGroup(
                *[
                    Dot(
                        pts[k],
                        radius=0.07,
                        color=colour,
                        fill_opacity=dot_op * (FAR_SIDE_OPACITY if _far_side(k) else 1),
                    )
                    for k in KEYPOINTS
                ]
            )
            herd.add(VGroup(edges, dots))
        return herd

    def video_frame(self, width_px=800):
        """Crop of the real recording around the top-lane mouse."""
        from manim import ImageMobject

        if self._frames is None:
            self._frames = load_video()
        f = self.frame.get_value()
        img = self._frames[min(round(f), len(self._frames) - 1)]
        _, cam = self._at(f)
        left = int(round(cam)) - width_px // 2
        padded = np.pad(img, ((0, 0), (width_px, width_px)), mode="edge")
        crop = padded[:, left + width_px : left + 2 * width_px]
        rgb = np.repeat(crop[:, :, None], 3, axis=2)
        mob = ImageMobject(rgb)
        s = self.scale.get_value()
        mob.width = width_px * s
        centre = self._to_scene(
            0, np.array(left + width_px / 2), np.array(VIDEO_HEIGHT / 2), cam
        )
        mob.move_to(centre)
        return mob.set_opacity(self.video.get_value())
