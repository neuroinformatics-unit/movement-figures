"""Downstream analysis on the tidy dataset, shown with movement's own plots."""

import numpy as np
from common import (
    DATASET_CENTRE,
    DATASET_SCALE,
    SMALL_DATASET_CENTRE,
    SMALL_DATASET_SCALE,
    arrow_label,
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
    FadeIn,
    FadeOut,
    GrowArrow,
    ImageMobject,
    Scene,
    ValueTracker,
    always_redraw,
    linear,
)
from vis_plots import render

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
        small_cube = (
            data_cube().scale(SMALL_DATASET_SCALE).move_to(SMALL_DATASET_CENTRE)
        )
        self.remove(labels)  # at once, so no afterimage trails the moving cube
        self.play(FadeOut(cap), cube.animate.become(small_cube), run_time=1.0)
        arrow = dataset_arrow(cube)
        clean = arrow_label("clean", arrow)
        self.play(GrowArrow(arrow), FadeIn(clean), run_time=0.8)
        cap = show_caption(self, "Drop outliers, smooth and interpolate tracks", 2.5)

        # --- Visualise: trajectory, then occupancy --------------------------
        paths, final = render(screen_pixels(PANEL_HEIGHT))
        frames = [ImageMobject(str(p)) for p in paths]
        for img in frames:
            img.height = PANEL_HEIGHT
            right_of(img.move_to(PANEL_CENTRE), arrow)
        step = ValueTracker(0)
        figure = always_redraw(lambda: frames[int(step.get_value())].copy())

        head, tail = split_caption(
            "Visualise trajectories and occupancy heatmaps", "Visualise trajectories"
        )
        self.play(FadeOut(cap), FadeIn(head), FadeIn(figure), run_time=0.6)
        self.play(
            step.animate.set_value(len(frames) - 1), run_time=3.0, rate_func=linear
        )
        figure.clear_updaters()
        occupancy = ImageMobject(str(final))
        occupancy.height = PANEL_HEIGHT
        right_of(occupancy.move_to(PANEL_CENTRE), arrow)
        self.play(FadeIn(tail), FadeIn(occupancy), run_time=0.8)
        self.remove(figure)
        self.wait(5.5)

        # Keep the dataset and arrow; the quantification segment relabels it
        keep = (corner, cube, arrow)
        self.play(*[FadeOut(m) for m in self.mobjects if m not in keep])
