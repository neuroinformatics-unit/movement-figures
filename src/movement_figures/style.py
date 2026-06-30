"""Layered, medium-aware matplotlib styling."""

from importlib.resources import files

import matplotlib.pyplot as plt

AVAILABLE_MEDIA: tuple[str, ...] = ("manuscript", "poster", "presentation")

_STYLE_DIR = files("movement_figures") / "styles"

# The medium of the most recent ``apply_style`` call; used by ``figure_size``.
_active_medium: str = "manuscript"

# ColorBrewer Set2 — movement's brand categorical palette (matches the base
# axes.prop_cycle in movement-base.mplstyle).
SET2: tuple[str, ...] = (
    "#66c2a5",
    "#fc8d62",
    "#8da0cb",
    "#e78ac3",
    "#a6d854",
    "#ffd92f",
    "#e5c494",
    "#b3b3b3",
)

# Semantic colors drawn from the cohesive Set2 / Dark2 / Pastel2 family.
PALETTE: dict[str, str] = {
    "primary": "#66c2a5",  # Set2 teal
    "secondary": "#fc8d62",  # Set2 orange
    "accent": "#e7298a",  # Dark2 magenta (vivid)
    "muted": "#b3b3b3",  # Set2 grey
    "highlight": "#f4cae4",  # Pastel2 pink (light marks on dark)
    "ink": "#666666",  # Dark2 grey (dark neutral)
}

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
