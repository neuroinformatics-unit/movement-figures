import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest

from movement_figures import AVAILABLE_MEDIA, FIGSIZES, PALETTE, apply_style


def test_available_media():
    assert AVAILABLE_MEDIA == ("manuscript", "poster", "presentation")


def test_apply_style_sets_medium_fontsize():
    apply_style("manuscript")
    assert plt.rcParams["font.size"] == 8
    apply_style("poster")
    assert plt.rcParams["font.size"] == 18


def test_apply_style_keeps_base_params():
    apply_style("presentation")
    assert plt.rcParams["axes.spines.top"] is False


def test_apply_style_default_is_manuscript():
    apply_style()
    assert plt.rcParams["font.size"] == 8


def test_apply_style_rejects_unknown_medium():
    with pytest.raises(ValueError):
        apply_style("billboard")


def test_palette_and_figsizes_shape():
    assert isinstance(PALETTE, dict) and len(PALETTE) >= 1
    assert set(FIGSIZES) == set(AVAILABLE_MEDIA)
    for sizes in FIGSIZES.values():
        for dims in sizes.values():
            assert len(dims) == 2
