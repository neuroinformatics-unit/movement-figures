"""Title card, a tracked video, and many formats becoming one tidy dataset."""

import numpy as np
from common import (
    DATASET_CENTRE,
    DATASET_SCALE,
    FONT,
    GREY,
    badge,
    chip,
    cube_labels,
    data_cube,
    image,
    show_caption,
)
from manim import (
    DOWN,
    LEFT,
    UP,
    FadeIn,
    FadeOut,
    Group,
    Scene,
    Text,
    always_redraw,
)
from mouse import Herd

# Playback rates for the 247 fps recording, slowed down to be legible
VIDEO_FPS = 14  # ~18x slow motion
RUN_FPS = 24  # ~10x slow motion

TOOLS = [
    ("DeepLabCut", "DLC_logo.png"),
    ("SLEAP", "SLEAP_logo.png"),
    ("LightningPose", "LightningPose_logo.png"),
    ("NWB", "NWB_logo.png"),
]


class Formats(Scene):
    def construct(self):
        # --- Title card -----------------------------------------------------
        logo = image("movement_logo_on-transparent.png", 3.7).shift(0.5 * UP)
        tagline = Text(
            "Python tools for analysing animal motion",
            font=FONT,
            font_size=52,
            color=GREY,
        ).next_to(logo, DOWN, buff=0.3)
        self.play(FadeIn(logo, scale=0.85), run_time=1.2)
        self.play(FadeIn(tagline, shift=0.2 * UP), run_time=0.8)
        self.wait(3.5)

        corner = badge()
        corner_logo, corner_url = corner
        self.play(
            FadeOut(tagline),
            logo.animate.scale(corner_logo.height / logo.height).move_to(corner_logo),
            run_time=1.2,
        )
        self.remove(logo)
        self.add(corner_logo)
        self.play(FadeIn(corner_url), run_time=0.5)

        # --- Real video → skeleton -----------------------------------------
        # The top lane is the real recording, zoomed in on the mouse
        herd = Herd(scale=0.015, centre=(0, -0.2), spacing=1.3)
        video = always_redraw(herd.video_frame)
        skeletons = always_redraw(herd.skeletons)
        self.add(video, skeletons)
        last_frame = herd.n_frames - 1

        def play_recording(fps, stop=last_frame):
            herd.frame.clear_updaters()
            herd.frame.add_updater(
                lambda m, dt: m.set_value(min(m.get_value() + fps * dt, stop))
            )
            self.add(herd.frame)  # updaters only run on mobjects in the scene

        play_recording(VIDEO_FPS)
        cap = show_caption(
            self,
            "Do you track animals with\nDeepLabCut, SLEAP or similar tools?",
            0,
        )
        self.play(herd.video.animate.set_value(1), run_time=0.8)
        self.wait(1.5)  # the video alone, so it reads as footage
        self.play(
            herd.dots[0].animate.set_value(1),
            herd.edges[0].animate.set_value(1),
            run_time=1.0,
        )
        self.wait(0.8)
        self.play(herd.video.animate.set_value(0), run_time=1.2)
        self.wait(2.5)  # the bare skeleton, to let the question sink in
        self.play(
            herd.dots[0].animate.set_value(0),
            herd.edges[0].animate.set_value(0),
            FadeOut(cap),
            run_time=0.6,
        )
        self.remove(video)

        # --- Many formats → mice run up to one tidy dataset ----------------
        run_scale, run_from, run_to = 0.0045, -1.2, 1.0  # mouse centre, in x
        herd.frame.clear_updaters()
        for tracker, value in (
            (herd.frame, 0),
            (herd.follow, 0),
            (herd.scale, run_scale),
            (herd.cx, run_from),
            (herd.cy, 1.25),
        ):
            tracker.set_value(value)
        # Stop the mice short of the dataset, so they end up side by side
        px_per_frame = np.diff(herd.camera_x).mean()
        stop_frame = (run_to - run_from) / (run_scale * px_per_frame)

        chips = Group(*[chip(name, logo) for name, logo in TOOLS])
        chips.arrange(DOWN, buff=0.2).to_edge(LEFT, buff=0.6).shift(0.35 * UP)
        cube = data_cube().scale(DATASET_SCALE).move_to(DATASET_CENTRE)
        cap = show_caption(
            self, "Bring tracks from all your favourite\ntools and file formats", 0
        )
        play_recording(RUN_FPS, stop=stop_frame)
        self.play(
            FadeIn(chips),
            *[t.animate.set_value(1) for t in herd.dots + herd.edges],
            run_time=0.6,
        )
        self.wait(1.4)
        cap = show_caption(self, "…into one tidy dataset", 0, previous=cap)
        self.play(FadeIn(cube, cube_labels(cube)), run_time=0.8)
        self.wait(4.5)

        # End on the dataset alone; the analysis segment continues from it
        herd.frame.clear_updaters()
        skeletons.clear_updaters()
        self.play(FadeOut(chips), FadeOut(skeletons))
