"""Shared style, helpers and building blocks for the showcase video."""

from pathlib import Path

import numpy as np
from manim import (
    RIGHT,
    UP,
    Group,
    Polygon,
    Rectangle,
    Text,
    VGroup,
)

from movement_figures.video import elements
from movement_figures.video.brand import (  # noqa: F401
    BG,
    FONT,
    GREY,
    LIGHT_GREY,
    use_brand_font_in_plots,
)
from movement_figures.video.brand import ORANGE as ORANGE
from movement_figures.video.brand import PURPLE as BLUE
from movement_figures.video.brand import TEAL as GREEN
from movement_figures.video.elements import (  # noqa: F401
    HEADER_HEIGHT,
    caption,
    caption_change,
    screen_pixels,
    show_caption,
    small_print,
    split_caption,
)

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"  # committed
INPUTS = ROOT / "inputs"  # not committed; listed in video.yml

MONO = "DejaVu Sans Mono"
PANEL = "#f1f1f1"
LOGO = ASSETS / "movement_logo_on-transparent.png"

# Front / top / side face tones for the three slabs of the data cube,
# matching the cube in the movement overview figures.
SLAB_TONES = {
    "green": ("#b3e2cd", "#8fb5a3", "#56705f"),
    "purple": ("#c9c7e8", "#a09eba", "#5f5d75"),
    "orange": ("#fdd0a8", "#b99273", "#6e5544"),
}


def image(name, height):
    """An image from ``assets/`` or ``inputs/``, ``height`` scene units tall."""
    path = ASSETS / name
    return elements.image(path if path.exists() else INPUTS / name, height)


def dataset_arrow(cube):
    """The arrow leading from the small dataset to the plots.

    Shared by the clean_viz and quantify segments, so it stays put
    across the cut.
    """
    from manim import Arrow

    start = cube.get_right() + 0.2 * RIGHT
    return Arrow(start, start + 1.33 * RIGHT, color=LIGHT_GREY, stroke_width=6, buff=0)


def right_of(mob, arrow, gap=0.1):
    """Place ``mob`` so its left edge sits just past the arrow's tip."""
    return mob.shift((arrow.get_right()[0] + gap - mob.get_left()[0]) * RIGHT)


# The title card's big logo, where the video starts and loops back to
TITLE_LOGO_HEIGHT = 3.7
TITLE_LOGO_CENTRE = 0.3 * UP


def badge():
    """Persistent header: the URL centred, the logo at the right."""
    return elements.badge(LOGO)


def svg_icon(name, height, colour=GREY):
    """A single-colour SVG icon from the assets, ``height`` scene units tall."""
    from manim import SVGMobject

    glyph = SVGMobject(str(ASSETS / name))
    glyph.set_fill(colour, opacity=1).set_stroke(width=0)
    glyph.height = height
    return glyph


def file_glyph(height=0.6, colour="#c4c4c4"):
    """Generic document icon (Font Awesome Free "file", CC BY 4.0)."""
    return svg_icon("file-solid-full.svg", height, colour)


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
# ...and where it waits, small, during the clean_viz and quantify segments
SMALL_DATASET_SCALE = 0.4
SMALL_DATASET_CENTRE = np.array([-5.7, 0.4, 0.0])
# The source clip plays as a thumbnail below the small dataset
THUMB_HEIGHT = 2.0
THUMB_CENTRE = SMALL_DATASET_CENTRE + np.array([0, -1.95, 0])


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
