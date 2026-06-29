import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from movement_figures import save_figure


def test_save_figure_writes_pdf_and_svg(tmp_path):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    paths = save_figure(fig, "demo", output_dir=tmp_path)
    names = {p.name for p in paths}
    assert names == {"demo.pdf", "demo.svg"}
    for p in paths:
        assert p.exists() and p.stat().st_size > 0


def test_save_figure_custom_formats(tmp_path):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    paths = save_figure(fig, "demo", formats=("svg",), output_dir=tmp_path)
    assert [p.name for p in paths] == ["demo.svg"]


def test_save_figure_creates_missing_dir(tmp_path):
    target = tmp_path / "nested" / "outputs"
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    save_figure(fig, "demo", output_dir=target)
    assert (target / "demo.pdf").exists()


def test_save_figure_is_deterministic(tmp_path):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    first = save_figure(fig, "d", output_dir=tmp_path / "a")
    second = save_figure(fig, "d", output_dir=tmp_path / "b")
    for p1, p2 in zip(first, second):
        assert p1.read_bytes() == p2.read_bytes(), f"{p1.name} not deterministic"
