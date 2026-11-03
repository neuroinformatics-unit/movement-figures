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


def test_plot_polar_histogram_rejects_uneven_bins(polar_ax):
    with pytest.raises(ValueError, match="divide 360"):
        plot_polar_histogram(xr.DataArray([0.0]), ax=polar_ax, bin_width_deg=25)
