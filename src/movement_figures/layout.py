"""Helpers for aligning axes in multi-panel figures."""

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from mpl_toolkits.axes_grid1 import make_axes_locatable

# Default colorbar strip geometry, shared so that a relocated colorbar and a
# reserved spacer shrink their host axes by exactly the same amount.
_CBAR_SIZE: str = "5%"
_CBAR_PAD: float = 0.1


def move_colorbar_to_divider(
    ax: Axes,
    label: str,
    size: str = _CBAR_SIZE,
    pad: float = _CBAR_PAD,
    anchor: str = "C",
) -> None:
    """Move an auto-generated colorbar into a divider axes beside ``ax``.

    The ``movement`` plotting helpers add colorbars via ``fig.colorbar(ax=ax)``,
    which steals width from the host axes. So an image panel with a colorbar
    ends up narrower than a colorbar-less one, breaking left/right alignment
    across a grid of panels. Relocating each colorbar into a fixed-size divider
    axes keeps every image panel's box identical. Pair this with
    :func:`reserve_colorbar_space` on a colorbar-less panel to keep it aligned
    too.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes whose colorbar should be relocated. Its first collection is
        assumed to carry the colorbar, as created by the ``movement`` plotting
        helpers.
    label : str
        Label for the relocated colorbar.
    size : str
        Width of the colorbar axes as a percentage of ``ax`` width.
    pad : float
        Padding between ``ax`` and the colorbar axes, in inches.
    anchor : str
        Compass anchor (e.g. ``"C"``, ``"W"``, ``"E"``) for placing an
        equal-aspect image within its divider cell. A divider overrides the
        axes-level anchor, so use this to e.g. left-justify (``"W"``) an image
        whose left edge must line up with another panel.
    """
    mappable = ax.collections[0]
    mappable.colorbar.remove()
    divider = make_axes_locatable(ax)
    divider.set_anchor(anchor)
    cax = divider.append_axes("right", size=size, pad=pad, axes_class=plt.Axes)
    ax.figure.colorbar(mappable, cax=cax, label=label)


def reserve_colorbar_space(
    ax: Axes,
    size: str = _CBAR_SIZE,
    pad: float = _CBAR_PAD,
    anchor: str = "C",
) -> None:
    """Reserve an invisible colorbar-sized strip beside ``ax``.

    Shrinks ``ax`` by the same amount a colorbar would, so a colorbar-less
    panel stays aligned with neighbouring panels that carry one via
    :func:`move_colorbar_to_divider`. Use matching ``size`` and ``pad``.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to shrink.
    size : str
        Width of the reserved strip as a percentage of ``ax`` width.
    pad : float
        Padding between ``ax`` and the reserved strip, in inches.
    anchor : str
        Compass anchor for placing an equal-aspect image within its divider
        cell; see :func:`move_colorbar_to_divider`. Match the paired
        colorbar panel so both stay aligned.
    """
    divider = make_axes_locatable(ax)
    divider.set_anchor(anchor)
    spacer = divider.append_axes("right", size=size, pad=pad, axes_class=plt.Axes)
    spacer.axis("off")
