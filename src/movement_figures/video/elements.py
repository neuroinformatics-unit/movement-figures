"""Building blocks for glanceable, silent videos: captions, credits, images
at their exact on-screen size, and the persistent header."""

from pathlib import Path

import numpy as np
from manim import (
    DOWN,
    RIGHT,
    UP,
    FadeIn,
    FadeOut,
    Group,
    ImageMobject,
    Succession,
    Text,
    VGroup,
    Wait,
    config,
)

from movement_figures.video.brand import FONT, GREY, LIGHT_GREY, TEAL

URL = "movement.neuroinformatics.dev"


def screen_pixels(height):
    """Pixel height, at the current render quality, of ``height`` scene units.

    Raster plots rendered at exactly this size need no rescaling by manim,
    which would otherwise alias fine lines and text.
    """
    return round(config.pixel_height * height / config.frame_height)


def image(path, height):
    """The image at ``path``, ``height`` scene units tall.

    The bitmap is resampled (Lanczos) to its exact on-screen size first;
    manim's own downscaling does not filter, so small logos would alias.
    Opaque images (logos on white) get a transparent background and are
    trimmed to their content; transparent ones are used as they are.
    """
    from PIL import Image

    src = Image.open(Path(path)).convert("RGBA")
    if src.getchannel("A").getextrema()[0] == 255:
        # Shave the canvas edges, where some logos have a thin frame or stray
        # pixels, then drop the near-white background: some logos sit on an
        # off-white canvas
        rgba = np.asarray(src)[3:-3, 3:-3].copy()
        rgba[rgba[..., :3].min(axis=2) >= 240, 3] = 0
        src = Image.fromarray(rgba)
        src = src.crop(src.getchannel("A").getbbox())
    px = screen_pixels(height)
    src = src.resize((max(1, round(src.width * px / src.height)), px), Image.LANCZOS)
    img = ImageMobject(np.asarray(src))
    img.height = height
    return img


def small_print(text):
    """Small print crediting data or icons."""
    return Text(text, font=FONT, font_size=16, color=LIGHT_GREY)


def caption(text, size=44, colour=GREY):
    """Lower-third subtitle, the main carrier of narration.

    Multi-line captions (separated by newlines) are centred line by line.
    """
    lines = VGroup(
        *[
            Text(line, font=FONT, font_size=size, color=colour)
            for line in text.split("\n")
        ]
    )
    return lines.arrange(DOWN, buff=0.12).to_edge(DOWN, buff=0.45)


def split_caption(full, head, size=44, colour=GREY):
    """A centred one-line caption, as (head, tail) glyph groups.

    Showing the head first and the tail later completes the sentence in place,
    without the head shifting to re-centre.
    """
    line = Text(full, font=FONT, font_size=size, color=colour)
    line.to_edge(DOWN, buff=0.45)
    n = len(head.replace(" ", ""))  # Text has no glyphs for spaces
    return line[:n], line[n:]


# Every caption change: the old one fades out fully before the new one
# fades in, rising slightly, so two captions never overlap
CAPTION_OUT, CAPTION_IN, CAPTION_RISE = 0.3, 0.5, 0.15


def caption_change(old=None, new=None, run_time=None):
    """Animation replacing caption ``old`` with ``new`` (either may be None).

    Given a longer ``run_time``, to share a ``play`` with longer animations,
    the change still takes its usual time, at the start.
    """
    parts = []
    if old is not None:
        parts.append(FadeOut(old, run_time=CAPTION_OUT))
    if new is not None:
        parts.append(FadeIn(new, shift=CAPTION_RISE * UP, run_time=CAPTION_IN))
    length = sum(part.run_time for part in parts)
    if run_time is not None:
        if run_time < length:
            raise ValueError(f"a caption change takes {length} s, not {run_time} s")
        if run_time > length:
            parts.append(Wait(run_time - length))
    return Succession(*parts)


def show_caption(scene, text, hold, previous=None, **kwargs):
    """Show a caption (replacing any previous one) and hold it."""
    new = caption(text, **kwargs)
    scene.play(caption_change(previous, new))
    if hold > 0:
        scene.wait(hold)
    return new


HEADER_HEIGHT = 0.75  # logo height; the header row spans this at the top


def badge(logo, url=URL):
    """Persistent header: ``url`` centred, the ``logo`` image at the right.

    Returns ``Group(logo, url)``, so any glance identifies the project.
    """
    logo = image(logo, HEADER_HEIGHT)
    logo.to_corner(UP + RIGHT, buff=0.25)
    url = Text(url, font=FONT, font_size=34, color=TEAL)
    url.move_to([0, logo.get_y(), 0])
    return Group(logo, url)
