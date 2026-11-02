"""movement's look in manim: Barlow, ColorBrewer Set2, a white background.

Importing this module registers the bundled Barlow with manim (Pango) and
sets the background, so no system-installed fonts are needed.
"""

from importlib.resources import files

import manimpango
from manim import config

from movement_figures.style import get_color

FONT = "Barlow"
TEAL = get_color("teal")
ORANGE = get_color("orange")
PURPLE = get_color("purple")
GREY = "#555555"
LIGHT_GREY = "#999999"
BG = "#ffffff"

for _path in (files("movement_figures") / "fonts").iterdir():
    if _path.name.startswith(FONT) and _path.name.endswith(".ttf"):
        manimpango.register_font(str(_path))

config.background_color = BG


def use_brand_font_in_plots():
    """Set matplotlib plots in Barlow, matching the captions.

    ``movement_figures.style`` already registered the bundled font with
    matplotlib on import.
    """
    import matplotlib.pyplot as plt

    plt.rcParams["font.family"] = FONT
