"""Shared style and helpers for movement research figures."""

from movement_figures.io import data_dir, save_figure
from movement_figures.layout import add_inset_colorbar
from movement_figures.style import (
    AVAILABLE_MEDIA,
    GOLDEN_RATIO,
    WIDTHS,
    Hue,
    Palette,
    apply_style,
    figure_size,
    get_color,
)

__all__ = [
    "AVAILABLE_MEDIA",
    "GOLDEN_RATIO",
    "Hue",
    "Palette",
    "WIDTHS",
    "add_inset_colorbar",
    "apply_style",
    "data_dir",
    "figure_size",
    "get_color",
    "save_figure",
]
