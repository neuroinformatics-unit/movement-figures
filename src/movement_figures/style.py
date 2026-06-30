"""Layered, medium-aware matplotlib styling."""

from importlib.resources import files

import matplotlib.pyplot as plt

AVAILABLE_MEDIA: tuple[str, ...] = ("manuscript", "poster", "presentation")

_STYLE_DIR = files("movement_figures") / "styles"

# Named colors aligned with movement branding (adjust hex values to taste).
PALETTE: dict[str, str] = {
    "primary": "#2a9d8f",
    "secondary": "#e76f51",
    "accent": "#264653",
    "muted": "#8d99ae",
}

# Figure dimensions in inches, per medium.
FIGSIZES: dict[str, dict[str, tuple[float, float]]] = {
    "manuscript": {"single": (3.5, 2.6), "double": (7.0, 4.0)},
    "poster": {"single": (8.0, 6.0), "double": (16.0, 9.0)},
    "presentation": {"single": (6.0, 4.0), "double": (12.0, 6.75)},
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
    if medium not in AVAILABLE_MEDIA:
        raise ValueError(f"Unknown medium {medium!r}; choose from {AVAILABLE_MEDIA}.")
    base = str(_STYLE_DIR / "movement-base.mplstyle")
    override = str(_STYLE_DIR / f"movement-{medium}.mplstyle")
    plt.style.use([base, override])
