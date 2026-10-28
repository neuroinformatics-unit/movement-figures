"""Shared style, helpers and building blocks for the SfN booth video."""

from pathlib import Path

import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    FadeIn,
    FadeOut,
    Group,
    ImageMobject,
    Polygon,
    RoundedRectangle,
    Text,
    VGroup,
    config,
)

ASSETS = Path(__file__).resolve().parent.parent / "assets"

# Brand: Barlow typeface, ColorBrewer Set2 colours
FONT = "Barlow"
MONO = "DejaVu Sans Mono"
GREEN = "#66c2a5"
BLUE = "#8da0cb"
ORANGE = "#fc8d62"
GREY = "#555555"
LIGHT_GREY = "#999999"
PANEL = "#f1f1f1"
BG = "#ffffff"

config.background_color = BG

# Front / top / side face tones for the three slabs of the data cube,
# matching the cube in the movement overview figures.
SLAB_TONES = {
    "green": ("#b3e2cd", "#8fb5a3", "#56705f"),
    "purple": ("#c9c7e8", "#a09eba", "#5f5d75"),
    "orange": ("#fdd0a8", "#b99273", "#6e5544"),
}


def image(name, height):
    img = ImageMobject(str(ASSETS / name))
    img.height = height
    return img


def caption(text, size=44, colour=GREY):
    """Lower-third subtitle, the main carrier of narration."""
    return Text(text, font=FONT, font_size=size, color=colour).to_edge(DOWN, buff=0.45)


def show_caption(scene, text, hold, previous=None, **kwargs):
    """Fade in a caption (replacing any previous one) and hold it."""
    new = caption(text, **kwargs)
    anims = [FadeIn(new, shift=0.15 * UP)]
    if previous is not None:
        anims.append(FadeOut(previous))
    scene.play(*anims, run_time=0.6)
    if hold > 0:
        scene.wait(hold)
    return new


def badge():
    """Persistent corner badge so any glance identifies the project."""
    logo = image("movement_logo_on-transparent.png", 0.95)
    url = Text(
        "movement.neuroinformatics.dev",
        font=FONT,
        font_size=20,
        color=LIGHT_GREY,
    )
    url.next_to(logo, DOWN, buff=0.02)
    return Group(logo, url).to_corner(UP + RIGHT, buff=0.25)


def file_glyph(colour=LIGHT_GREY, height=0.6):
    """Generic dog-eared document icon for formats without a logo."""
    w, h, ear = 0.75, 1.0, 0.28
    outline = Polygon(
        [0, 0, 0],
        [w, 0, 0],
        [w, h - ear, 0],
        [w - ear, h, 0],
        [0, h, 0],
        color=colour,
        stroke_width=4,
    )
    fold = Polygon(
        [w - ear, h, 0],
        [w - ear, h - ear, 0],
        [w, h - ear, 0],
        color=colour,
        stroke_width=4,
    )
    glyph = VGroup(outline, fold)
    glyph.height = height
    return glyph


def chip(label, logo=None, extensions="", width=4.9, height=0.8):
    """A software/format card: logo (or file glyph), name and extensions."""
    box = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.14,
        fill_color=PANEL,
        fill_opacity=1,
        stroke_width=0,
    )
    icon = image(logo, height * 0.72) if logo else file_glyph(height=height * 0.66)
    if icon.width > height * 0.95:
        icon.width = height * 0.95
    icon.move_to(box.get_left() + RIGHT * (0.2 + height * 0.48))
    name = Text(label, font=FONT, font_size=30, color=GREY)
    name.next_to(icon, RIGHT, buff=0.25)
    parts = [box, icon, name]
    if extensions:
        ext = Text(extensions, font=MONO, font_size=20, color=LIGHT_GREY)
        ext.move_to(box.get_right() + LEFT * (0.2 + ext.width / 2))
        parts.append(ext)
    return Group(*parts)


def slab(tone, rows=4, cols=2, depth=6, cell=0.36, dv=(0.27, 0.17)):
    """One isometric slab of the data cube (one individual).

    Front face: time (rows) x space (cols); depth runs along keypoints.
    """
    front_c, top_c, side_c = SLAB_TONES[tone]
    dv = np.array([*dv, 0.0])
    stroke = {"stroke_color": "#4a4a4a", "stroke_width": 1.2}
    cells = VGroup()

    def quad(p, a, b, colour):
        return Polygon(
            p, p + a, p + a + b, p + b, fill_color=colour, fill_opacity=1, **stroke
        )

    right, down = np.array([cell, 0, 0]), np.array([0, -cell, 0])
    for c in range(cols):
        for k in range(depth):
            cells.add(quad(np.array([c * cell, 0, 0]) + k * dv, right, dv, top_c))
    for r in range(rows):
        for k in range(depth):
            p = np.array([cols * cell, -r * cell, 0]) + k * dv
            cells.add(quad(p, dv, down, side_c))
    for r in range(rows):
        for c in range(cols):
            p = np.array([c * cell, -r * cell, 0])
            cells.add(quad(p, right, down, front_c))
    return cells


def data_cube(offset=(0.62, -0.55)):
    """Three stacked slabs, back (green) to front (orange)."""
    offset = np.array([*offset, 0.0])
    slabs = [slab(t) for t in ("green", "purple", "orange")]
    for i, s in enumerate(slabs):
        s.shift(i * offset)
    return VGroup(*slabs).move_to(np.zeros(3))


def slab_corners(s, rows=4, cols=2, depth=6):
    """Key corners of a slab built by `slab`, valid after any transform."""
    n_top, n_side = cols * depth, rows * depth

    def front(r, c):
        return s[n_top + n_side + r * cols + c].get_vertices()

    return {
        "front_tl": front(0, 0)[0],
        "front_bl": front(rows - 1, 0)[3],
        "front_br": front(rows - 1, cols - 1)[2],
        "far_bottom": s[n_top + (rows - 1) * depth + depth - 1].get_vertices()[2],
        "far_top": s[(cols - 1) * depth + depth - 1].get_vertices()[2],
    }
