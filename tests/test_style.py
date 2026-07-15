from typing import get_args

import matplotlib.pyplot as plt
import pytest
import seaborn as sns
from matplotlib.colors import to_hex
from matplotlib.font_manager import FontProperties, findfont

from movement_figures import (
    AVAILABLE_MEDIA,
    WIDTHS,
    Hue,
    Palette,
    apply_style,
    figure_size,
    get_color,
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
    set2 = sns.color_palette("Set2", 8).as_hex()
    assert [to_hex(c) for c in cycle] == [to_hex(c) for c in set2]


def test_hue_and_palette_members():
    assert get_args(Hue) == (
        "teal",
        "orange",
        "purple",
        "pink",
        "green",
        "yellow",
        "brown",
        "gray",
    )
    assert get_args(Palette) == ("Set2", "Dark2", "Pastel2")


def test_get_color_defaults_to_set2():
    assert get_color("teal") == "#66c2a5"


@pytest.mark.parametrize(
    ("hue_name", "palette", "expected"),
    [
        ("teal", "Set2", "#66c2a5"),
        ("orange", "Set2", "#fc8d62"),
        ("gray", "Set2", "#b3b3b3"),
        ("teal", "Dark2", "#1b9e77"),
        ("pink", "Dark2", "#e7298a"),
        ("pink", "Pastel2", "#f4cae4"),
    ],
)
def test_get_color_returns_expected_hex(hue_name, palette, expected):
    assert get_color(hue_name, palette) == expected


def test_get_color_covers_every_hue():
    for palette in get_args(Palette):
        expected = sns.color_palette(palette, len(get_args(Hue))).as_hex()
        for i, hue_name in enumerate(get_args(Hue)):
            assert get_color(hue_name, palette) == expected[i]


@pytest.mark.parametrize(
    ("medium", "expected_font_file"),
    [
        ("manuscript", "LiberationSans-Regular.ttf"),
        ("presentation", "LiberationSans-Regular.ttf"),
        ("poster", "Barlow-Regular.ttf"),
    ],
)
def test_apply_style_resolves_to_bundled_font(medium, expected_font_file):
    """Each medium must resolve to a font we ship, not a system fallback."""
    apply_style(medium)
    resolved = findfont(FontProperties(family=["sans-serif"]))
    assert resolved.endswith(expected_font_file)


def test_apply_style_keeps_base_params():
    apply_style("presentation")
    assert plt.rcParams["axes.spines.top"] is False


def test_apply_style_default_is_manuscript():
    apply_style()
    assert plt.rcParams["font.size"] == 8


def test_apply_style_rejects_unknown_medium():
    with pytest.raises(ValueError):
        apply_style("billboard")


def test_widths_shape():
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
