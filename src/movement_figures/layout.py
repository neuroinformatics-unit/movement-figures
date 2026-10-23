"""Helpers for aligning axes in multi-panel figures."""

from matplotlib.axes import Axes

# Default inset colorbar geometry, as fractions of the host axes' width.
_INSET_CBAR_WIDTH: float = 0.05
_INSET_CBAR_PAD: float = 0.03


def add_inset_colorbar(
    ax: Axes,
    label: str,
    width: float = _INSET_CBAR_WIDTH,
    pad: float = _INSET_CBAR_PAD,
) -> Axes:
    """Move an auto-generated colorbar into an inset axes beside ``ax``.

    The ``movement`` plotting helpers add colorbars via ``fig.colorbar(ax=ax)``,
    which steals width from the host axes and breaks alignment across panels.
    An inset axes placed just outside ``ax`` leaves the host box untouched, so
    every image panel keeps the same size without reserving space on the
    colorbar-less ones. It also works with constrained layout (the default in
    this package's style), which accounts for the inset when laying out the
    figure.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes whose colorbar should be relocated. Its first collection is
        assumed to carry the colorbar, as created by the ``movement`` plotting
        helpers.
    label : str
        Label for the relocated colorbar.
    width : float
        Width of the colorbar as a fraction of ``ax`` width.
    pad : float
        Gap between ``ax`` and the colorbar as a fraction of ``ax`` width.

    Returns
    -------
    matplotlib.axes.Axes
        The colorbar axes.
    """
    mappable = ax.collections[0]
    mappable.colorbar.remove()
    cax = ax.inset_axes((1 + pad, 0, width, 1))
    ax.figure.colorbar(mappable, cax=cax, label=label)
    return cax
