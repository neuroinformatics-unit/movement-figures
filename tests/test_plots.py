import matplotlib.pyplot as plt
import numpy as np
import pytest
import xarray as xr

from movement_figures import plot_polar_histogram


@pytest.fixture
def polar_ax():
    fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
    yield ax
    plt.close(fig)


def test_plot_polar_histogram(polar_ax):
    angles = xr.DataArray(
        np.array([0.1, 0.2, np.pi / 2, np.nan]),
        dims="time",
        coords={"individual": "id_0"},  # scalar coord: xarray would title it
    )
    plot_polar_histogram(angles, ax=polar_ax, bin_width_deg=30)

    assert len(polar_ax.patches) == 12
    assert polar_ax.get_title() == ""
    labels = [t.get_text() for t in polar_ax.get_xticklabels()]
    assert labels == ["0°", "45°", "90°", "135°", "180°", "-135°", "-90°", "-45°"]


def test_plot_polar_histogram_tick_step(polar_ax):
    plot_polar_histogram(xr.DataArray([0.0]), ax=polar_ax, tick_step_deg=90)

    labels = [t.get_text() for t in polar_ax.get_xticklabels()]
    assert labels == ["0°", "90°", "180°", "-90°"]


@pytest.mark.parametrize("step", ["bin_width_deg", "tick_step_deg"])
def test_plot_polar_histogram_rejects_uneven_steps(polar_ax, step):
    with pytest.raises(ValueError, match=f"{step} must divide 360"):
        plot_polar_histogram(xr.DataArray([0.0]), ax=polar_ax, **{step: 25})
