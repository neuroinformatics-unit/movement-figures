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
    ORANGE,
    SMALL_DATASET_CENTRE,
    SMALL_DATASET_SCALE,
    badge,
    caption,
    caption_change,
    cube_labels,
    data_cube,
    dataset_arrow,
    right_of,
    screen_pixels,
    small_print,
    split_caption,
)
from manim import (
    DL,
    DOWN,
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
PLAYBACK = 3  # times real time


class CleanViz(Scene):
    def construct(self):
        corner = badge()
        cube = data_cube().scale(DATASET_SCALE).move_to(DATASET_CENTRE)
        labels = cube_labels(cube)
        # Picks up exactly where the io segment ends
        cap = caption("…into one tidy dataset")
        self.add(corner, cube, labels, cap)
        self.wait(0.5)

        # --- The dataset moves aside ---------------------------------------
        small_cube = (
            data_cube().scale(SMALL_DATASET_SCALE).move_to(SMALL_DATASET_CENTRE)
        )
        self.remove(labels)  # at once, so no afterimage trails the moving cube
        self.play(
            caption_change(cap, run_time=1.0),
            cube.animate.become(small_cube),
            run_time=1.0,
        )

        arrow = dataset_arrow(cube)
        paths, fractions = render(screen_pixels(PANEL_HEIGHT))
        series_axes, raw_lines, clean_lines, trajectory, occupancy = [
            right_of(
                ImageMobject(str(p)).set(height=PANEL_HEIGHT).move_to(PANEL_CENTRE),
                arrow,
            )
            for p in paths
        ]
        x0, y0 = trajectory.get_corner(DL)[:2]
        w, h = trajectory.width, trajectory.height

        # --- Clean: the raw tracks, then the cleaned snout beside them -----
        # The clip plays where the trajectory plot's maze will be
        left, bottom, width, height = (
            x0 + fractions[0][0] * w,
            y0 + fractions[0][1] * h,
            fractions[0][2] * w,
            fractions[0][3] * h,
        )
        frames, poses, keypoints = video_clip(screen_pixels(height))
        edges = [(keypoints.index(a), keypoints.index(b)) for a, b in SKELETON]
        px = height / VIDEO_HEIGHT  # scene units per video pixel
        step = ValueTracker(0)  # clip frame index

        def to_scene(p):
            return np.array(
                [left + (p[0] - MAZE_CROP[0]) * px, bottom + height - p[1] * px, 0]
            )

        def video():
            img = ImageMobject(
                np.repeat(frames[int(step.get_value())][..., None], 3, axis=2)
            )
            img.height = height
            return img.move_to([left + width / 2, bottom + height / 2, 0])

        def skeleton():
            pts = poses[int(step.get_value())]
            group = VGroup()
            for a, b in edges:
                group.add(
                    Line(
                        to_scene(pts[a]),
                        to_scene(pts[b]),
                        color=ORANGE,
                        stroke_width=3,
                    )
                )
            for p in pts:
                group.add(Dot(to_scene(p), radius=0.03, color=ORANGE))
            return group

        # The cleaning plot's lines unfold left to right: each line's layer,
        # hidden over the axes beyond the ``progress`` (0 to 1) made so far
        rows, cols = raw_lines.pixel_array.shape[:2]
        series_left, series_bottom, series_width, series_height = fractions[2]
        first_col = round(series_left * cols)
        last_col = round((series_left + series_width) * cols)
        top_row = round((1 - series_bottom - series_height) * rows)
        bottom_row = round((1 - series_bottom) * rows)

        def unfolding(lines, progress):
            def draw():
                col = first_col + round(progress() * (last_col - first_col))
                img = lines.pixel_array.copy()
                img[top_row:bottom_row, col:, 3] = 0
                return ImageMobject(img).replace(lines).set_z_index(lines.z_index)

            return always_redraw(draw)

        shown_seconds = len(frames) * CLIP_STEP / VIDEO_FPS
        clip = always_redraw(video)
        overlay = always_redraw(skeleton)
        # The raw line keeps pace with the clip
        raw_unfolding = unfolding(
            raw_lines, lambda: step.get_value() * CLIP_STEP / VIDEO_FPS / shown_seconds
        )
        data_credit = small_print("Data: Loukia Katsouri").next_to(clip, DOWN, buff=0.1)
        cap = caption("Plot keypoint positions over time")
        self.play(
            GrowArrow(arrow),
            caption_change(new=cap, run_time=0.8),
            *[
                FadeIn(m)
                for m in (clip, overlay, series_axes, raw_unfolding, data_credit)
            ],
            run_time=0.8,
        )
        self.play(
            step.animate.set_value(len(frames) - 1),
            run_time=shown_seconds / PLAYBACK,
            rate_func=linear,
        )
        for m in (clip, overlay, raw_unfolding):
            m.clear_updaters()
        # The last clip frame is a step short of the window's end
        self.remove(raw_unfolding)
        self.add(raw_lines)

        # The cleaned line, over the raw one so that shows only where cleaning
        # moved it, sweeps across faster as the caption appears
        new_cap = caption("Drop outliers, smooth and interpolate")
        sweep = ValueTracker(0)
        clean_lines.set_z_index(1)
        clean_unfolding = unfolding(clean_lines, sweep.get_value)
        self.add(clean_unfolding)
        self.play(
            caption_change(cap, new_cap, run_time=1.5),
            sweep.animate.set_value(1),
            run_time=1.5,
            rate_func=linear,
        )
        clean_unfolding.clear_updaters()
        self.remove(clean_unfolding)
        self.add(clean_lines)
        cap = new_cap
        self.wait(3.5)
        shown = [clip, overlay, series_axes, raw_lines, clean_lines, data_credit]

        # --- Visualise: trajectory, then occupancy --------------------------
        head, tail = split_caption(
            "Visualise trajectories and occupancy heatmaps", "Visualise trajectories"
        )
        self.play(
            caption_change(cap, head, run_time=1.2),
            *[FadeOut(m) for m in shown],
            FadeIn(trajectory),
            run_time=1.2,
        )
        self.wait(2.0)
        self.play(
            caption_change(new=tail, run_time=0.8), FadeIn(occupancy), run_time=0.8
        )
        self.remove(trajectory)
        self.wait(3.0)

        # Keep the dataset and arrow; the quantify segment reuses them
        keep = (corner, cube, arrow)
        self.play(*[FadeOut(m) for m in self.mobjects if m not in keep])
