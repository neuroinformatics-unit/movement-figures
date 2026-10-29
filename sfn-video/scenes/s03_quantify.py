"""Quantify motion: two bees and metrics computed with movement."""

import numpy as np
from bee_plots import render
from bees import ARENA, COLOURS, FPS, load_clean, skeleton_edges, video_frames
from common import (
    SMALL_DATASET_CENTRE,
    SMALL_DATASET_SCALE,
    THUMB_CENTRE,
    THUMB_HEIGHT,
    badge,
    data_cube,
    dataset_arrow,
    right_of,
    screen_pixels,
    show_caption,
)
from manim import (
    Dot,
    FadeIn,
    FadeOut,
    ImageMobject,
    Line,
    Scene,
    ValueTracker,
    VGroup,
    always_redraw,
    linear,
)

# The dataset and arrow stay where the clean_viz segment left them; the bee
# clip plays as a thumbnail below the dataset, the plots fill the right
FIGURE_CENTRE = np.array([2.0, -0.2, 0])
FIGURE_HEIGHT = 5.6
PLAYBACK = 1.5  # times real time
CAPTION = "Quantify motion any way you like"


class Quantify(Scene):
    def construct(self):
        corner = badge()
        # Picks up exactly where the clean_viz segment ends
        cube = data_cube().scale(SMALL_DATASET_SCALE).move_to(SMALL_DATASET_CENTRE)
        arrow = dataset_arrow(cube)
        self.add(corner, cube, arrow)

        frames = video_frames()
        position = load_clean().transpose("time", "individual", "keypoint", "space")
        xy = position.values
        keypoints = list(position.keypoint.values)
        edge_idx = [
            (keypoints.index(a), keypoints.index(b)) for a, b in skeleton_edges()
        ]

        step = ValueTracker(0)  # recorded frame index
        x0, y0, size = ARENA

        def video():
            img = ImageMobject(
                np.repeat(frames[int(step.get_value())][..., None], 3, axis=2)
            )
            img.height = THUMB_HEIGHT
            return img.move_to(THUMB_CENTRE)

        def to_scene(p):
            left = THUMB_CENTRE[0] - THUMB_HEIGHT / 2
            top = THUMB_CENTRE[1] + THUMB_HEIGHT / 2
            return np.array(
                [
                    left + (p[0] - x0) / size * THUMB_HEIGHT,
                    top - (p[1] - y0) / size * THUMB_HEIGHT,
                    0,
                ]
            )

        def skeletons():
            """Edges and keypoints, styled like the travelator mice."""
            t = min(int(step.get_value()), len(xy) - 1)
            group = VGroup()
            for bee, colour in enumerate(COLOURS):
                pts = xy[t, bee]
                for a, b in edge_idx:
                    if not np.isnan(pts[[a, b]]).any():
                        group.add(
                            Line(
                                to_scene(pts[a]),
                                to_scene(pts[b]),
                                color=colour,
                                stroke_width=2,
                            )
                        )
                for p in pts:
                    if not np.isnan(p).any():
                        group.add(Dot(to_scene(p), radius=0.018, color=colour))
            return group

        clip = always_redraw(video)
        overlay = always_redraw(skeletons)

        # --- The source clip plays as a thumbnail -------------------------
        # One caption for the whole segment, while the plots build up
        show_caption(self, CAPTION, 0)
        self.play(FadeIn(clip), FadeIn(overlay), run_time=0.6)
        self.play(
            step.animate.set_value(len(frames) - 1),
            run_time=len(frames) / (FPS * PLAYBACK),
            rate_func=linear,
        )
        clip.clear_updaters()
        overlay.clear_updaters()

        # --- Metrics, one panel at a time ---------------------------------
        stages = []
        for path in render(screen_pixels(FIGURE_HEIGHT)):
            img = ImageMobject(str(path))
            img.height = FIGURE_HEIGHT
            stages.append(right_of(img.move_to(FIGURE_CENTRE), arrow))

        shown = None
        for stage in stages:
            self.play(FadeIn(stage), run_time=0.6)
            if shown is not None:
                self.remove(shown)
            shown = stage
            self.wait(2.5)
        self.wait(2.0)

        # Fade to the header alone; the gui segment continues from it
        self.play(*[FadeOut(m) for m in self.mobjects if m is not corner])
