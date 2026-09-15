"""Shared style and helpers for movement research figures."""

from movement_figures.io import data_dir, save_figure
from movement_figures.layout import (
    move_colorbar_to_divider,
    reserve_colorbar_space,
)
from movement_figures.napari_utils import napari_canvas_screenshot
from movement_figures.style import (
    AVAILABLE_MEDIA,
    WIDTHS,
    Hue,
    Palette,
    apply_style,
    figure_size,
    get_color,
)

__all__ = [
    "AVAILABLE_MEDIA",
    "Hue",
    "Palette",
    "WIDTHS",
    "apply_style",
    "data_dir",
    "figure_size",
    "get_color",
    "move_colorbar_to_divider",
    "napari_canvas_screenshot",
    "reserve_colorbar_space",
    "save_figure",
]
