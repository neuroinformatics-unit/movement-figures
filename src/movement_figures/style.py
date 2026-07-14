"""Layered, medium-aware matplotlib styling."""

from importlib.resources import files
from typing import Literal, get_args

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager

AVAILABLE_MEDIA: tuple[str, ...] = ("manuscript", "poster", "presentation")

_STYLE_DIR = files("movement_figures") / "styles"
_FONT_DIR = files("movement_figures") / "fonts"


def _register_bundled_fonts() -> None:
    """Make the fonts shipped with this package visible to matplotlib.

    Without this, matplotlib only sees system-installed fonts, so the same
    figure picks up a different typeface on each machine (and on CI).
    """
    for path in _FONT_DIR.iterdir():
        if path.name.endswith(".ttf"):
            font_manager.fontManager.addfont(str(path))


_register_bundled_fonts()

# The medium of the most recent ``apply_style`` call; used by ``figure_size``.
_active_medium: str = "manuscript"

# Qualitative (categorical) palettes from ColorBrewer used in movement's brand identity.
Palette = Literal["Set2", "Dark2", "Pastel2"]

# Assign names to the 8 hues used in all the above palettes
Hue = Literal["teal", "orange", "purple", "pink", "green", "yellow", "brown", "gray"]

# Precompute each palette's hex colors (in hue order) and each hue's index
# Both are derived from the Literals above.
_PALETTES: dict[Palette, list[str]] = {
    name: sns.color_palette(name, len(get_args(Hue))).as_hex()
    for name in get_args(Palette)
}
_HUE_INDEX: dict[Hue, int] = {hue: i for i, hue in enumerate(get_args(Hue))}


def get_color(hue_name: Hue, palette: Palette = "Set2") -> str:
    """Return the hex color for a named hue from a given palette."""
    return _PALETTES[palette][_HUE_INDEX[hue_name]]


# Standardized figure widths (inches) per medium and column span. Heights are
# chosen per figure via figure_size(..., height=...).
WIDTHS: dict[str, dict[str, float]] = {
    "manuscript": {"single": 3.5, "double": 7.0},
    "poster": {"single": 8.0, "double": 16.0},
    "presentation": {"single": 6.0, "double": 12.0},
}


def apply_style(medium: str = "manuscript") -> None:
    """Apply the shared base style plus a medium-specific override.

    Parameters
    ----------
    medium : str
        One of ``AVAILABLE_MEDIA``. Defaults to ``"manuscript"``.

    Raises
    ------
    ValueError
        If ``medium`` is not a known medium.
    """
    global _active_medium
    if medium not in AVAILABLE_MEDIA:
        raise ValueError(f"Unknown medium {medium!r}; choose from {AVAILABLE_MEDIA}.")
    base = str(_STYLE_DIR / "movement-base.mplstyle")
    override = str(_STYLE_DIR / f"movement-{medium}.mplstyle")
    plt.style.use([base, override])
    _active_medium = medium


def figure_size(width: str = "double", height: float = 4.0) -> tuple[float, float]:
    """Return a ``(width, height)`` figure size in inches.

    The width is the standardized width for the active medium (set by the most
    recent :func:`apply_style` call) and the given column ``width`` (``"single"``
    or ``"double"``). ``height`` is chosen freely per figure.
    """
    return (WIDTHS[_active_medium][width], height)
