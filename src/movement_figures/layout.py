"""Helpers for aligning axes in multi-panel figures."""

from typing import Literal

from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.layout_engine import PlaceHolderLayoutEngine
from matplotlib.transforms import blended_transform_factory

# Default inset colorbar geometry, as fractions of the host axes' width.
_INSET_CBAR_WIDTH: float = 0.05
_INSET_CBAR_PAD: float = 0.03


def add_inset_colorbar(
    ax: Axes,
    label: str,
    width: float = _INSET_CBAR_WIDTH,
    pad: float = _INSET_CBAR_PAD,
    side: Literal["left", "right"] = "right",
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
    side : {"left", "right"}
        Side of ``ax`` on which to place the colorbar. Its ticks and label
        face away from ``ax``.

    Returns
    -------
    matplotlib.axes.Axes
        The colorbar axes.
    """
    if side not in ("left", "right"):
        raise ValueError(f"side must be 'left' or 'right', not {side!r}")
    mappable = ax.collections[0]
    mappable.colorbar.remove()
    x0 = 1 + pad if side == "right" else -pad - width
    cax = ax.inset_axes((x0, 0, width, 1))
    ax.figure.colorbar(mappable, cax=cax, label=label)
    cax.yaxis.set_ticks_position(side)
    cax.yaxis.set_label_position(side)
    return cax


def freeze_layout(fig: Figure) -> None:
    """Fix every axes of ``fig`` where the layout engine has placed it.

    Constrained layout re-positions all axes on every draw, undoing any
    position set by hand. Freezing it lets you fine-tune a few axes, e.g.
    with ``ax.set_position``, starting from the automatic layout.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure to freeze. Add all its content first, since the layout is
        no longer updated afterwards.
    """
    fig.canvas.draw()  # runs the layout engine
    fig.set_layout_engine("none")


def align_y_labels(*axes: Axes) -> None:
    """Put the y-axis labels of ``axes`` at the same horizontal position.

    Each label sits just beyond its axes' tick labels, so axes with wider
    tick labels push their label further out. This moves all the labels to
    the outermost position among them, so axes stacked above one another
    have their labels in one vertical line. Unlike matplotlib's
    ``Figure.align_ylabels``, it works for any axes, including inset
    colorbars that aren't part of the figure's grid.

    Parameters
    ----------
    *axes : matplotlib.axes.Axes
        Axes of one figure, with their y-axis labels on the left.
        Their positions must be final: call :func:`freeze_layout` first if
        the figure uses a layout engine.
    """
    fig = axes[0].figure
    engine = fig.get_layout_engine()
    if engine is not None and not isinstance(engine, PlaceHolderLayoutEngine):
        raise RuntimeError("Call freeze_layout(fig) before align_y_labels.")
    if any(ax.yaxis.get_label_position() != "left" for ax in axes):
        raise ValueError("align_y_labels only handles y-axis labels on the left.")

    fig.canvas.draw()  # places each label next to its tick labels

    def label_x(ax: Axes) -> float:
        """Horizontal position of ``ax``'s y-axis label, as a figure fraction."""
        label = ax.yaxis.label
        display_xy = label.get_transform().transform(label.get_position())
        return fig.transFigure.inverted().transform(display_xy)[0]

    outermost_x = min(label_x(ax) for ax in axes)
    for ax in axes:
        # x as a figure fraction (shared by all labels), y centred on the axes
        figure_x_axes_y = blended_transform_factory(fig.transFigure, ax.transAxes)
        ax.yaxis.set_label_coords(outermost_x, 0.5, transform=figure_x_axes_y)
