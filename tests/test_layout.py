import matplotlib.pyplot as plt
import numpy as np
import pytest

from movement_figures import (
    add_inset_colorbar,
    align_y_labels,
    apply_style,
    freeze_layout,
)


@pytest.mark.parametrize("side", ["right", "left"])
def test_add_inset_colorbar_keeps_panels_aligned(side):
    apply_style()
    fig, (ax_left, ax_right) = plt.subplots(1, 2)
    data = np.random.default_rng(0).random((8, 10))
    ax_left.pcolormesh(data)
    mesh = ax_right.pcolormesh(data)
    fig.colorbar(mesh, ax=ax_right)  # mimics the movement plotting helpers
    for ax in (ax_left, ax_right):
        ax.set_aspect("equal")

    cax = add_inset_colorbar(ax_right, "label", side=side)
    fig.canvas.draw()

    left, right = ax_left.get_position(), ax_right.get_position()
    assert left.width == pytest.approx(right.width)
    assert left.height == pytest.approx(right.height)
    assert cax.get_ylabel() == "label"
    assert cax.yaxis.get_label_position() == side
    cbar_box = cax.get_position()
    if side == "right":
        assert cbar_box.x0 >= right.x1
    else:
        assert cbar_box.x1 <= right.x0
    renderer = fig.canvas.get_renderer()
    cbar_extent = cax.get_tightbbox(renderer)
    assert cbar_extent.x1 <= fig.bbox.x1
    assert cbar_extent.x0 >= ax_left.get_tightbbox(renderer).x1


def test_add_inset_colorbar_rejects_unknown_side():
    fig, ax = plt.subplots()
    mesh = ax.pcolormesh(np.zeros((2, 2)))
    fig.colorbar(mesh, ax=ax)
    with pytest.raises(ValueError, match="side"):
        add_inset_colorbar(ax, "label", side="top")


def test_freeze_layout_keeps_positions_set_by_hand():
    apply_style()
    fig, (ax_top, ax_bottom) = plt.subplots(2, 1)
    fig.canvas.draw()
    automatic = ax_bottom.get_position().bounds

    freeze_layout(fig)
    assert ax_bottom.get_position().bounds == pytest.approx(automatic)
    ax_bottom.set_position([0.2, 0.1, 0.5, 0.3])
    fig.canvas.draw()
    assert ax_bottom.get_position().bounds == pytest.approx((0.2, 0.1, 0.5, 0.3))


def _y_label_x0(ax):
    renderer = ax.figure.canvas.get_renderer()
    return ax.yaxis.label.get_window_extent(renderer).x0


def test_align_y_labels_moves_labels_to_the_outermost():
    apply_style()
    fig, (ax_wide, ax_narrow) = plt.subplots(2, 1)
    ax_wide.set_ylim(0, 100_000)  # wide tick labels push its label out
    ax_narrow.set_ylim(0, 1)
    for ax in (ax_wide, ax_narrow):
        ax.set_ylabel("label")
    freeze_layout(fig)
    assert _y_label_x0(ax_wide) < _y_label_x0(ax_narrow) - 1

    align_y_labels(ax_wide, ax_narrow)
    fig.canvas.draw()
    outermost = _y_label_x0(ax_wide)
    assert _y_label_x0(ax_narrow) == pytest.approx(outermost)


def test_align_y_labels_requires_a_frozen_layout():
    apply_style()
    fig, axes = plt.subplots(2, 1)
    with pytest.raises(RuntimeError, match="freeze_layout"):
        align_y_labels(*axes)
