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

# (colour, frame offset, horizontal stagger in px), top lane first
INDIVIDUALS = [(GREEN, 0, 30), (BLUE, 22, -40), (ORANGE, 44, 10)]
MAX_OFFSET = max(offset for _, offset, _ in INDIVIDUALS)

PIX_CY = 142  # vertical pixel coordinate mapped to a lane's centre
GROUND = 203  # paw contact level on the travelator, in pixels
GRID = 48  # spacing of the backdrop grid, in pixels
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


class Herd:
    """Three walking skeletons in stacked lanes, driven by value trackers.

    ``frame`` scrubs through the (interpolated) recording, ``scale`` maps
    pixels to scene units, ``cx``/``cy`` place the middle lane and
    ``spacing`` sets the distance between lanes.
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
        self.lines = ValueTracker(0)
        self.grid = ValueTracker(0)

    def _at(self, f):
        i = min(int(np.floor(f)), len(self.pos) - 2)
        w = f - i
        p = (1 - w) * self.pos[i] + w * self.pos[i + 1]
        c = (1 - w) * self.camera_x[i] + w * self.camera_x[i + 1]
        return p, c

    def _to_scene(self, lane, px, py, cam):
        s = self.scale.get_value()
        _, _, stagger = INDIVIDUALS[lane]
        x = self.cx.get_value() + s * (px - cam + stagger)
        y = (
            self.cy.get_value()
            + (1 - lane) * self.spacing.get_value()
            - s * (py - PIX_CY)
        )
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
            pts = dict(zip(KEYPOINTS, self.keypoints(lane), strict=True))
            edges = VGroup(
                *[
                    Line(
                        pts[a],
                        pts[b],
                        color=colour,
                        stroke_width=6,
                        stroke_opacity=self.lines.get_value()
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
                        fill_opacity=FAR_SIDE_OPACITY if _far_side(k) else 1,
                    )
                    for k in KEYPOINTS
                ]
            )
            herd.add(VGroup(edges, dots))
        return herd

    def backdrop(self, half_width=7.6):
        from manim import Line, VGroup

        op = self.grid.get_value()
        s = self.scale.get_value()
        span = half_width / s
        lines = VGroup()
        grid = {"color": "#e0e0e0", "stroke_width": 2, "stroke_opacity": op}
        ground = {"color": "#b0b0b0", "stroke_width": 4, "stroke_opacity": op}
        top, bottom = GROUND - 2 * GRID, GROUND
        for lane in range(len(INDIVIDUALS)):
            _, cam = self._lane_frame(lane, None)
            stagger = INDIVIDUALS[lane][2]
            left, right = cam - stagger - span, cam - stagger + span
            for x in np.arange(np.ceil(left / GRID) * GRID, right, GRID):
                a, b = self._to_scene(
                    lane, np.array([x, x]), np.array([top, bottom]), cam
                )
                lines.add(Line(a, b, **grid))
            for y, style in ((top, grid), (top + GRID, grid), (bottom, ground)):
                a, b = self._to_scene(
                    lane, np.array([left, right]), np.array([y, y]), cam
                )
                lines.add(Line(a, b, **style))
        return lines
