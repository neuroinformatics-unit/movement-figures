import matplotlib.pyplot as plt
import pytest
from matplotlib.colors import to_hex

from movement_figures import (
    AVAILABLE_MEDIA,
    PALETTE,
    SET2,
    WIDTHS,
    apply_style,
    figure_size,
)


def test_available_media():
    assert AVAILABLE_MEDIA == ("manuscript", "poster", "presentation")


def test_apply_style_manuscript_fontsize():
    apply_style("manuscript")
    assert plt.rcParams["font.size"] == 8


def test_apply_style_poster_fontsize():
    apply_style("poster")
    assert plt.rcParams["font.size"] == 24


def test_apply_style_color_cycle_matches_set2():
    apply_style("poster")
    cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    assert [to_hex(c) for c in cycle] == [to_hex(c) for c in SET2]


def test_palette_keys():
    assert set(PALETTE) == {
        "primary",
        "secondary",
        "accent",
        "muted",
        "highlight",
        "ink",
    }


def test_apply_style_keeps_base_params():
    apply_style("presentation")
    assert plt.rcParams["axes.spines.top"] is False


def test_apply_style_default_is_manuscript():
    apply_style()
    assert plt.rcParams["font.size"] == 8


def test_apply_style_rejects_unknown_medium():
    with pytest.raises(ValueError):
        apply_style("billboard")


def test_palette_and_widths_shape():
    assert isinstance(PALETTE, dict) and len(PALETTE) >= 1
    assert set(WIDTHS) == set(AVAILABLE_MEDIA)
    for spans in WIDTHS.values():
        assert set(spans) == {"single", "double"}
        for w in spans.values():
            assert isinstance(w, (int, float))


def test_figure_size_uses_active_medium():
    apply_style("poster")
    assert figure_size("double", height=5.0) == (16.0, 5.0)
    apply_style("manuscript")
    assert figure_size("single", height=2.6) == (3.5, 2.6)
