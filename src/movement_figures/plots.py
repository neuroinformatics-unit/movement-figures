"""Reusable plotting helpers for movement figures."""

from typing import Any

import numpy as np
import xarray as xr
from matplotlib.projections.polar import PolarAxes

from movement_figures.style import get_color


def plot_polar_histogram(
    da: xr.DataArray,
    ax: PolarAxes,
    bin_width_deg: float = 15,
    **hist_kwargs: Any,
) -> PolarAxes:
    """Plot a polar histogram of angles in the shared movement-figures style.

    Angles increase clockwise from 0° at the right, matching image
    coordinates (y points down), as in ``movement``'s
    `head direction example <https://movement.neuroinformatics.dev/latest/examples/compute_head_direction.html>`_.
    Ticks are every 45° and labelled in (-180°, 180°].

    Parameters
    ----------
    da : xarray.DataArray
        Angles in radians, in [-pi, pi]. NaNs are ignored.
    ax : matplotlib.projections.polar.PolarAxes
        Axes created with ``projection="polar"``.
    bin_width_deg : float
        Width of each bin in degrees. Must divide 360.
    **hist_kwargs
        Forwarded to :meth:`xarray.DataArray.plot.hist`, overriding the
        defaults (density, teal fill, white bin edges).

    Returns
    -------
    matplotlib.projections.polar.PolarAxes
        The axes, with no title or radial tick labels.

    Raises
    ------
    ValueError
        If ``bin_width_deg`` does not divide 360.
    """
    if 360 % bin_width_deg:
        raise ValueError(f"bin_width_deg must divide 360, got {bin_width_deg}.")
    n_bins = int(360 / bin_width_deg)
    kwargs = {
        "density": True,
        "color": get_color("teal", "Set2"),
        "edgecolor": "white",
        "linewidth": 1.0,
        **hist_kwargs,
    }
    da.plot.hist(bins=np.linspace(-np.pi, np.pi, n_bins + 1), ax=ax, **kwargs)

    ax.set_theta_direction(-1)
    ax.set_theta_offset(0)
    ax.set_xlabel("")
    ax.set_yticklabels([])
    ax.set_title("")  # xarray titles the plot after scalar coords

    ticks_deg = np.arange(0, 360, 45)
    ax.set_xticks(np.linspace(0, 2 * np.pi, len(ticks_deg), endpoint=False))
    ax.set_xticklabels(
        [f"{t if t <= 180 else t - 360}\N{DEGREE SIGN}" for t in ticks_deg]
    )
    return ax
