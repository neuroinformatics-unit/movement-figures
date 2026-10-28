"""Downstream analysis on the tidy dataset, shown with movement's own plots."""

import numpy as np
from common import (
    DATASET_CENTRE,
    DATASET_SCALE,
    FONT,
    GREY,
    LIGHT_GREY,
    badge,
    caption,
    cube_labels,
    data_cube,
    show_caption,
)
from manim import (
    RIGHT,
    UP,
    Arrow,
    FadeIn,
    FadeOut,
    GrowArrow,
    ImageMobject,
    Scene,
    Text,
    ValueTracker,
    always_redraw,
    linear,
)
from vis_plots import render

SMALL_CUBE_CENTRE = np.array([-5.7, 0.4, 0])
PANEL_CENTRE = np.array([1.8, -0.1, 0])
PANEL_HEIGHT = 5.4


class Analysis(Scene):
    def construct(self):
        corner = badge()
        cube = data_cube().scale(DATASET_SCALE).move_to(DATASET_CENTRE)
        labels = cube_labels(cube)
        # Picks up exactly where the formats segment ends
        cap = caption("…into one tidy dataset")
        self.add(corner, cube, labels, cap)
        self.wait(0.5)

        # --- Clean: the dataset moves aside, an arrow leads on --------------
        small_cube = data_cube().scale(0.4).move_to(SMALL_CUBE_CENTRE)
        self.remove(labels)  # at once, so no afterimage trails the moving cube
        self.play(FadeOut(cap), cube.animate.become(small_cube), run_time=1.0)
        arrow = Arrow(
            cube.get_right() + 0.2 * RIGHT,
            cube.get_right() + 1.6 * RIGHT,
            color=LIGHT_GREY,
            stroke_width=6,
            buff=0,
        )
        clean = Text("clean", font=FONT, font_size=32, color=GREY)
        clean.next_to(arrow, UP, buff=0.15)
        self.play(GrowArrow(arrow), FadeIn(clean), run_time=0.8)
        cap = show_caption(self, "Drop outliers, smooth and interpolate tracks", 2.5)

        # --- Visualise: trajectory, then occupancy --------------------------
        paths, final = render()
        frames = [ImageMobject(str(p)) for p in paths]
        for img in frames:
            img.height = PANEL_HEIGHT
            img.move_to(PANEL_CENTRE)
        step = ValueTracker(0)
        figure = always_redraw(lambda: frames[int(step.get_value())].copy())

        cap = show_caption(self, "Visualise trajectories", 0, previous=cap)
        self.play(FadeIn(figure), run_time=0.6)
        self.play(
            step.animate.set_value(len(frames) - 1), run_time=3.0, rate_func=linear
        )
        figure.clear_updaters()
        occupancy = ImageMobject(str(final))
        occupancy.height = PANEL_HEIGHT
        occupancy.move_to(PANEL_CENTRE)
        cap = show_caption(
            self, "Visualise trajectories and occupancy heatmaps", 0, previous=cap
        )
        self.play(FadeIn(occupancy), run_time=0.8)
        self.remove(figure)
        self.wait(5.5)

        # Fade to the badge alone, so the loop restarts cleanly
        self.play(*[FadeOut(m) for m in self.mobjects if m is not corner])
        self.wait(0.5)
