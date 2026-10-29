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
    small_print,
)
from manim import (
    DOWN,
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
# clip plays large, then as a thumbnail below the dataset; the plots fill the
# right
FIGURE_CENTRE = np.array([2.0, 0.2, 0])
FIGURE_HEIGHT = 5.6
PLAYBACK = 2.0  # times real time
# The clip at first: as tall as the plots, a little higher to leave room for
# its credit above the caption
VIDEO_HEIGHT = 5.2
VIDEO_Y = 0.15
VIDEO_OVER = 0.33  # across the figure: roughly over the speed and distance plots
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

        stages = []
        for path in render(screen_pixels(FIGURE_HEIGHT)):
            img = ImageMobject(str(path))
            img.height = FIGURE_HEIGHT
            stages.append(right_of(img.move_to(FIGURE_CENTRE), arrow))

        step = ValueTracker(0)  # recorded frame index
        x0, y0, size = ARENA
        # The clip first plays large, where the plots will be, then shrinks
        # to a thumbnail below the dataset to make room for them
        big_height = VIDEO_HEIGHT
        big_x = stages[0].get_left()[0] + VIDEO_OVER * stages[0].width
        big_centre = np.array([big_x, VIDEO_Y, 0])
        shrink = ValueTracker(0)

        def placement():
            a = shrink.get_value()
            height = (1 - a) * big_height + a * THUMB_HEIGHT
            return height, (1 - a) * big_centre + a * THUMB_CENTRE

        def video():
            height, centre = placement()
            img = ImageMobject(
                np.repeat(frames[int(step.get_value())][..., None], 3, axis=2)
            )
            img.height = height
            return img.move_to(centre)

        def skeletons():
            """Edges and keypoints, styled like the travelator mice."""
            height, centre = placement()
            # Lines thicken less than the clip grows, or they would crowd it
            scale = np.sqrt(height / THUMB_HEIGHT)
            left, top = centre[0] - height / 2, centre[1] + height / 2

            def to_scene(p):
                return np.array(
                    [
                        left + (p[0] - x0) / size * height,
                        top - (p[1] - y0) / size * height,
                        0,
                    ]
                )

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
                                stroke_width=2 * scale,
                            )
                        )
                for p in pts:
                    if not np.isnan(p).any():
                        group.add(Dot(to_scene(p), radius=0.018 * scale, color=colour))
            return group

        clip = always_redraw(video)
        overlay = always_redraw(skeletons)
        data_credit = small_print("Data: Pereira et al., Nature Methods, 2022")
        data_credit.next_to(clip, DOWN, buff=0.1)

        # --- The source clip plays large ------------------------------------
        # One caption for the whole segment, while the plots build up
        show_caption(self, CAPTION, 0)
        self.play(FadeIn(clip), FadeIn(overlay), FadeIn(data_credit), run_time=0.6)
        self.play(
            step.animate.set_value(len(frames) - 1),
            run_time=len(frames) / (FPS * PLAYBACK),
            rate_func=linear,
        )

        # --- It shrinks below the dataset as the metrics appear -------------
        self.play(
            shrink.animate.set_value(1),
            FadeOut(data_credit),
            FadeIn(stages[0]),
            run_time=1.2,
        )
        clip.clear_updaters()
        overlay.clear_updaters()
        self.wait(3.0)
        self.play(FadeIn(stages[1]), run_time=0.6)
        self.remove(stages[0])
        self.wait(4.0)

        # Fade to the header alone; the gui segment continues from it
        self.play(*[FadeOut(m) for m in self.mobjects if m is not corner])
