import warnings

import matplotlib.pyplot as plt
import pytest

from movement_figures import data_dir, save_figure
from movement_figures.io import _default_output_dir


def test_save_figure_default_writes_pdf(tmp_path):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    paths = save_figure(fig, "demo", output_dir=tmp_path)
    assert [p.name for p in paths] == ["demo.pdf"]
    assert paths[0].exists() and paths[0].stat().st_size > 0


def test_save_figure_writes_png(tmp_path):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    paths = save_figure(fig, "demo", formats=("png",), output_dir=tmp_path)
    assert [p.name for p in paths] == ["demo.png"]
    assert paths[0].exists() and paths[0].stat().st_size > 0


def test_save_figure_custom_formats(tmp_path):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    paths = save_figure(fig, "demo", formats=("svg",), output_dir=tmp_path)
    assert [p.name for p in paths] == ["demo.svg"]
    assert paths[0].exists() and paths[0].stat().st_size > 0


def test_save_figure_creates_missing_dir(tmp_path):
    target = tmp_path / "nested" / "outputs"
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    paths = save_figure(fig, "demo", output_dir=target)
    assert [p.name for p in paths] == ["demo.pdf"]
    assert paths[0].exists() and paths[0].stat().st_size > 0


def test_save_figure_is_deterministic(tmp_path):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    first = save_figure(fig, "d", output_dir=tmp_path / "a")
    second = save_figure(fig, "d", output_dir=tmp_path / "b")
    for p1, p2 in zip(first, second, strict=True):
        assert p1.read_bytes() == p2.read_bytes(), f"{p1.name} not deterministic"


def test_default_output_dir_is_project_root_outputs():
    d = _default_output_dir()
    assert d.name == "outputs"
    assert (d.parent / "pyproject.toml").is_file()


def test_data_dir_is_project_root_data():
    d = data_dir()
    assert d.name == "data"
    assert (d.parent / "pyproject.toml").is_file()


def test_data_dir_independent_of_cwd(monkeypatch):
    root = data_dir().parent  # project root (has pyproject.toml)
    monkeypatch.chdir(root / "figures")
    assert data_dir() == root / "data"


def test_default_output_dir_independent_of_cwd(monkeypatch):
    root = _default_output_dir().parent  # project root (has pyproject.toml)
    # Simulate interactive execution from inside the figures/ directory.
    monkeypatch.chdir(root / "figures")
    assert _default_output_dir() == root / "outputs"


def test_save_figure_keeps_figure_size(tmp_path):
    fig, ax = plt.subplots(figsize=(3.5, 2.0))
    ax.plot([0, 1], [0, 1])
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        (path,) = save_figure(
            fig, "demo", formats=("png",), output_dir=tmp_path, dpi=100
        )
    height_px, width_px = plt.imread(path).shape[:2]
    assert (width_px, height_px) == (350, 200)


def test_save_figure_warns_on_tight_bbox(tmp_path):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    with pytest.warns(UserWarning, match="bbox_inches='tight'"):
        save_figure(fig, "demo", output_dir=tmp_path, bbox_inches="tight")
