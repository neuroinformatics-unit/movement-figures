"""Shared style, helpers and building blocks for the SfN booth video."""

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
    Polygon,
    Rectangle,
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


def screen_pixels(height):
    """Pixel height, at the current render quality, of ``height`` scene units.

    Raster plots rendered at exactly this size need no rescaling by manim,
    which would otherwise alias fine lines and text.
    """
    return round(config.pixel_height * height / config.frame_height)


def image(name, height):
    """An asset image, ``height`` scene units tall.

    The bitmap is resampled (Lanczos) to its exact on-screen size first;
    manim's own downscaling does not filter, so small logos would alias.
    """
    from PIL import Image

    src = Image.open(ASSETS / name).convert("RGBA")
    px = screen_pixels(height)
    src = src.resize((max(1, round(src.width * px / src.height)), px), Image.LANCZOS)
    img = ImageMobject(np.asarray(src))
    img.height = height
    return img


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


def dataset_arrow(cube):
    """The arrow leading from the small dataset to the analysis plots.

    Shared by the analysis and quantification segments, so it stays put
    across the cut while only its label changes.
    """
    from manim import Arrow

    start = cube.get_right() + 0.2 * RIGHT
    return Arrow(start, start + 2.0 * RIGHT, color=LIGHT_GREY, stroke_width=6, buff=0)


def arrow_label(text, arrow):
    """A label centred above ``arrow``."""
    return Text(text, font=FONT, font_size=32, color=GREY).next_to(arrow, UP, 0.15)


def right_of(mob, arrow, gap=0.1):
    """Place ``mob`` so its left edge sits just past the arrow's tip."""
    return mob.shift((arrow.get_right()[0] + gap - mob.get_left()[0]) * RIGHT)


def split_caption(full, head, size=44, colour=GREY):
    """A centred one-line caption, as (head, tail) glyph groups.

    Showing the head first and the tail later completes the sentence in place,
    without the head shifting to re-centre.
    """
    line = Text(full, font=FONT, font_size=size, color=colour)
    line.to_edge(DOWN, buff=0.45)
    n = len(head.replace(" ", ""))  # Text has no glyphs for spaces
    return line[:n], line[n:]


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


HEADER_HEIGHT = 0.75  # logo height; the header row spans this at the top


def badge():
    """Persistent header: the URL centred, the logo at the right.

    Returns ``Group(logo, url)``, so any glance identifies the project.
    """
    logo = image("movement_logo_on-transparent.png", HEADER_HEIGHT)
    logo.to_corner(UP + RIGHT, buff=0.25)
    url = Text(
        "movement.neuroinformatics.dev",
        font=FONT,
        font_size=34,
        color=GREEN,
    )
    url.move_to([0, logo.get_y(), 0])
    return Group(logo, url)


def file_glyph(height=0.6, colour="#c4c4c4"):
    """Generic document icon (Font Awesome Free "file", CC BY 4.0)."""
    from manim import SVGMobject

    glyph = SVGMobject(str(ASSETS / "file-solid-full.svg"))
    glyph.set_fill(colour, opacity=1).set_stroke(width=0)
    glyph.height = height
    return glyph


def chip(label, logo, height=0.9):
    """A tool's logo and name in a fixed-size row, so rows align and space
    evenly whatever each logo's shape."""
    slot = Rectangle(width=height, height=height, stroke_width=0, fill_opacity=0)
    icon = image(logo, height * 0.68)
    if icon.width > height:
        icon.width = height
    icon.move_to(slot)
    name = Text(label, font=FONT, font_size=30, color=GREY)
    name.next_to(slot, RIGHT, buff=0.25)
    return Group(slot, icon, name)


def more_chip(height=0.9):
    """A trailing row hinting at further formats, laid out like a ``chip``."""
    slot = Rectangle(width=height, height=height, stroke_width=0, fill_opacity=0)
    icon = file_glyph(height=height * 0.68).move_to(slot)
    name = Text("and more…", font=FONT, font_size=30, color=GREY)
    name.next_to(slot, RIGHT, buff=0.25)
    return Group(slot, icon, name)


def slab(tone, rows=4, cols=2, depth=6, cell=0.36):
    """One isometric slab of the data cube (one individual).

    Light face: time (rows) x space (cols), receding down-right; dark face:
    time x keypoints (depth), receding up-right.
    """
    front_c, top_c, side_c = SLAB_TONES[tone]
    stroke = {"stroke_color": "#808080", "stroke_width": 1.4}
    cells = VGroup()

    def quad(p, a, b, colour):
        return Polygon(
            p, p + a, p + a + b, p + b, fill_color=colour, fill_opacity=1, **stroke
        )

    u, v, down = (
        cell * np.array([np.cos(np.pi / 6), -0.5, 0]),
        cell * np.array([np.cos(np.pi / 6), 0.5, 0]),
        cell * np.array([0, -1.0, 0]),
    )
    for c in range(cols):
        for k in range(depth):
            cells.add(quad(c * u + k * v, u, v, top_c))
    for r in range(rows):
        for k in range(depth):
            cells.add(quad(cols * u + k * v + r * down, v, down, side_c))
    for r in range(rows):
        for c in range(cols):
            cells.add(quad(c * u + r * down, u, down, front_c))
    return cells


# Where the tidy dataset sits when segment 1 hands over to segment 2
DATASET_SCALE = 0.8
DATASET_CENTRE = np.array([4.1, -0.1, 0.0])
# ...and where it waits, small, during the analysis segments
SMALL_DATASET_SCALE = 0.4
SMALL_DATASET_CENTRE = np.array([-5.7, 0.4, 0.0])


def data_cube(gap=2.75, cell=0.36):
    """Three slabs side by side along the space axis, as in data_icon.png.

    ``gap`` is the spacing between slabs, in cells along the space axis.
    """
    u = cell * np.array([np.cos(np.pi / 6), -0.5, 0])
    slabs = [slab(t, cell=cell) for t in ("green", "purple", "orange")]
    for i, s in enumerate(slabs):
        s.shift(i * gap * u)
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


def _along(text, a, b, normal_shift):
    """Place text parallel to segment a->b, offset perpendicular to it."""
    d = b - a
    text.rotate(np.arctan2(d[1], d[0]))
    n = np.array([-d[1], d[0], 0]) / np.linalg.norm(d)
    return text.move_to((a + b) / 2 + normal_shift * n)


def cube_labels(cube):
    """Dimension labels around the data cube, as in the overview figure."""
    back, _, front = cube
    bc, fc = slab_corners(back), slab_corners(front)
    style = {"font": MONO, "font_size": 24, "color": LIGHT_GREY}
    time = _along(Text("time", **style), bc["front_bl"], bc["front_tl"], 0.25)
    space = _along(Text("space", **style), bc["front_bl"], fc["front_br"], -0.3)
    keypoints = _along(
        Text("keypoints", **style), fc["front_br"], fc["far_bottom"], -0.28
    )
    individuals = Text("individuals", font=MONO, font_size=24)
    individuals.set_color_by_gradient(GREEN, BLUE, ORANGE)
    _along(individuals, bc["far_top"], fc["far_top"], 0.3)
    return VGroup(time, space, keypoints, individuals)
