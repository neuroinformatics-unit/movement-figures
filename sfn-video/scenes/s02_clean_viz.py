"""Cleaning and visualising the tidy dataset, with movement's own plots."""

import numpy as np
from clean_viz_plots import (
    CLIP_STEP,
    MAZE_CROP,
    SKELETON,
    VIDEO_FPS,
    VIDEO_HEIGHT,
    render,
    video_clip,
)
from common import (
    DATASET_CENTRE,
    DATASET_SCALE,
    GREEN,
    SMALL_DATASET_CENTRE,
    SMALL_DATASET_SCALE,
    THUMB_CENTRE,
    THUMB_HEIGHT,
    badge,
    caption,
    cube_labels,
    data_cube,
    dataset_arrow,
    right_of,
    screen_pixels,
    show_caption,
    split_caption,
)
from manim import (
    Dot,
    FadeIn,
    FadeOut,
    GrowArrow,
    ImageMobject,
    Line,
    Scene,
    ValueTracker,
    VGroup,
    always_redraw,
    linear,
)

PANEL_CENTRE = np.array([1.8, -0.1, 0])
PANEL_HEIGHT = 5.4
PLAYBACK = 4  # times real time


class CleanViz(Scene):
    def construct(self):
        corner = badge()
        cube = data_cube().scale(DATASET_SCALE).move_to(DATASET_CENTRE)
        labels = cube_labels(cube)
        # Picks up exactly where the io segment ends
        cap = caption("…into one tidy dataset")
        self.add(corner, cube, labels, cap)
        self.wait(0.5)

        # --- The dataset moves aside; its source clip plays below it -------
        small_cube = (
            data_cube().scale(SMALL_DATASET_SCALE).move_to(SMALL_DATASET_CENTRE)
        )
        self.remove(labels)  # at once, so no afterimage trails the moving cube
        self.play(FadeOut(cap), cube.animate.become(small_cube), run_time=1.0)

        frames, poses, keypoints = video_clip()
        edges = [(keypoints.index(a), keypoints.index(b)) for a, b in SKELETON]
        step = ValueTracker(0)  # thumbnail frame index
        px = THUMB_HEIGHT / VIDEO_HEIGHT  # scene units per video pixel
        left = THUMB_CENTRE[0] - (MAZE_CROP[1] - MAZE_CROP[0]) * px / 2
        top = THUMB_CENTRE[1] + THUMB_HEIGHT / 2

        def to_scene(p):
            return np.array([left + (p[0] - MAZE_CROP[0]) * px, top - p[1] * px, 0])

        def thumbnail():
            img = ImageMobject(
                np.repeat(frames[int(step.get_value())][..., None], 3, axis=2)
            )
            img.height = THUMB_HEIGHT
            return img.move_to(THUMB_CENTRE)

        def skeleton():
            pts = poses[int(step.get_value())]
            group = VGroup()
            for a, b in edges:
                if not np.isnan(pts[[a, b]]).any():
                    group.add(
                        Line(
                            to_scene(pts[a]),
                            to_scene(pts[b]),
                            color=GREEN,
                            stroke_width=2,
                        )
                    )
            for p in pts:
                if not np.isnan(p).any():
                    group.add(Dot(to_scene(p), radius=0.018, color=GREEN))
            return group

        video = always_redraw(thumbnail)
        overlay = always_redraw(skeleton)
        cap = show_caption(self, "Drop outliers, smooth and interpolate tracks", 0)
        self.play(FadeIn(video), FadeIn(overlay), run_time=0.6)
        self.play(
            step.animate.set_value(len(frames) - 1),
            run_time=len(frames) * CLIP_STEP / (VIDEO_FPS * PLAYBACK),
            rate_func=linear,
        )
        video.clear_updaters()
        overlay.clear_updaters()

        # --- Clean: an arrow leads to raw vs cleaned tracks ----------------
        arrow = dataset_arrow(cube)
        cleaning, trajectory, occupancy = [
            right_of(
                ImageMobject(str(p)).set(height=PANEL_HEIGHT).move_to(PANEL_CENTRE),
                arrow,
            )
            for p in render(screen_pixels(PANEL_HEIGHT))
        ]
        self.play(GrowArrow(arrow), FadeIn(cleaning), run_time=0.8)
        self.wait(3.5)

        # --- Visualise: trajectory, then occupancy --------------------------
        head, tail = split_caption(
            "Visualise trajectories and occupancy heatmaps", "Visualise trajectories"
        )
        self.play(
            FadeOut(cap),
            FadeIn(head),
            FadeOut(cleaning),
            FadeIn(trajectory),
            run_time=0.6,
        )
        self.wait(2.0)
        self.play(FadeIn(tail), FadeIn(occupancy), run_time=0.8)
        self.remove(trajectory)
        self.wait(5.5)

        # Keep the dataset and arrow; the quantify segment reuses them
        keep = (corner, cube, arrow)
        self.play(*[FadeOut(m) for m in self.mobjects if m not in keep])
