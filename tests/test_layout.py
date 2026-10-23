import matplotlib.pyplot as plt
import numpy as np
import pytest

from movement_figures import add_inset_colorbar, apply_style


def test_add_inset_colorbar_keeps_panels_aligned():
    apply_style()
    fig, (ax_left, ax_right) = plt.subplots(1, 2)
    data = np.random.default_rng(0).random((8, 10))
    ax_left.pcolormesh(data)
    mesh = ax_right.pcolormesh(data)
    fig.colorbar(mesh, ax=ax_right)  # mimics the movement plotting helpers
    for ax in (ax_left, ax_right):
        ax.set_aspect("equal")

    cax = add_inset_colorbar(ax_right, "label")
    fig.canvas.draw()

    left, right = ax_left.get_position(), ax_right.get_position()
    assert left.width == pytest.approx(right.width)
    assert left.height == pytest.approx(right.height)
    assert cax.get_ylabel() == "label"
    # Constrained layout must keep the colorbar inside the canvas.
    renderer = fig.canvas.get_renderer()
    assert cax.get_tightbbox(renderer).x1 <= fig.bbox.x1
