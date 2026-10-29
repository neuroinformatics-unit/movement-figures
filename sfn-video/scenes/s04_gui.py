"""Python scripts or the napari GUI, then a screen recording of the GUI."""

import subprocess

import numpy as np
from common import (
    ASSETS,
    badge,
    caption_change,
    image,
    screen_pixels,
    show_caption,
)
from manim import (
    LEFT,
    RIGHT,
    UP,
    FadeIn,
    FadeOut,
    ImageMobject,
    Rectangle,
    Scene,
    ValueTracker,
    always_redraw,
    config,
)

RECORDING = ASSETS / "movement_napari_bees_workflow_2026-10-29.mp4"
RECORDING_FPS = 30
PLAYBACK = 1.6  # times real time
# The recording plays on black, so its dark UI blends in; captions go light
BACKDROP = "#000000"
CAPTION_ON_BACKDROP = "#dddddd"
CACHE = ASSETS.parent / "cache" / "gui"
# Between the header URL (bottom at y=3.2; the logo sits clear to the right)
# and a one-line caption (top at y=-2.99), with a small margin to each
VIDEO_HEIGHT = 5.9
VIDEO_CENTRE = np.array([0, 0.1, 0])
THUMB_HEIGHT = 2.4  # beside the Python logo, before it grows
# Recording time (s) at which each caption takes over
CHAPTERS = [
    (0.0, "Interactively explore motion tracks"),
    (10.0, "Identify and fix tracking errors"),
    (24.0, "Define regions of interest"),
]


def recording_frames(height_px):
    """Paths to the recording's frames, resized to ``height_px``."""
    out = CACHE / f"{height_px}px"
    if not out.exists():
        out.mkdir(parents=True)
        subprocess.run(
            [
                "ffmpeg",
                "-loglevel",
                "error",
                "-i",
                str(RECORDING),
                "-vf",
                f"scale=-2:{height_px}:flags=lanczos",
                "-q:v",
                "2",
                str(out / "%04d.jpg"),
            ],  # fmt: skip
            check=True,
        )
    return sorted(out.glob("*.jpg"))


class GUI(Scene):
    def construct(self):
        corner = badge()
        # Picks up where the quantify segment ends: the header alone
        self.add(corner)

        # --- Python scripts, or the GUI --------------------------------------
        python = image("python-logo-generic.png", 1.5).move_to(0.3 * UP + 3.2 * LEFT)
        cap = show_caption(self, "You can call movement from Python scripts", 0)
        self.play(FadeIn(python), run_time=0.6)
        self.wait(1.5)

        # The GUI is the recording itself: a playing thumbnail beside the
        # Python logo, which then grows to its place
        frames = recording_frames(screen_pixels(VIDEO_HEIGHT))
        clock = ValueTracker(0)  # recording time (s)
        clock.add_updater(lambda m, dt: m.increment_value(PLAYBACK * dt))
        end = (len(frames) - 1) / RECORDING_FPS
        thumb_centre = 0.3 * UP + 3.2 * RIGHT
        grow = ValueTracker(0)

        def video_frame():
            i = min(int(clock.get_value() * RECORDING_FPS), len(frames) - 1)
            img = ImageMobject(str(frames[i]))
            a = grow.get_value()
            img.height = (1 - a) * THUMB_HEIGHT + a * VIDEO_HEIGHT
            return img.move_to((1 - a) * thumb_centre + a * VIDEO_CENTRE)

        video = always_redraw(video_frame)
        backdrop = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            fill_color=BACKDROP,
            fill_opacity=1,
            stroke_width=0,
        ).set_z_index(-1)  # behind the header

        cap = show_caption(self, "…and use our GUI", 0, previous=cap)
        self.add(clock)  # the recording plays on through captions and waits
        self.play(FadeIn(video), run_time=0.6)
        self.wait(1.0)
        self.play(
            grow.animate.set_value(1),
            FadeOut(python),
            caption_change(cap, run_time=1.2),
            FadeIn(backdrop),
            run_time=1.2,
        )

        def wait_until(t):
            """Wait until recording time ``t``."""
            if t - clock.get_value() > PLAYBACK / RECORDING_FPS:
                self.wait((t - clock.get_value()) / PLAYBACK)

        cap = None
        for start, text in CHAPTERS:
            wait_until(start)
            cap = show_caption(self, text, 0, previous=cap, colour=CAPTION_ON_BACKDROP)
        wait_until(end)
        clock.clear_updaters()
        video.clear_updaters()
        self.wait(0.5)

        # Fade back to white, with the header alone; the community segment
        # continues from it
        self.play(*[FadeOut(m) for m in self.mobjects if m is not corner])
