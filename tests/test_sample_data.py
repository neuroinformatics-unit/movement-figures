from movement_figures.sample_data import (
    discover_sample_data_specs,
    prefetch_sample_data,
    read_sample_data_specs,
)


def test_read_sample_data_specs_parses_frontmatter(tmp_path):
    qmd = tmp_path / "example.qmd"
    qmd.write_text(
        """---
title: Example
sample_data:
  - filename: first.h5
    with_video: true
  - filename: second.csv
---

body
""",
        encoding="utf-8",
    )

    assert read_sample_data_specs(qmd) == [("first.h5", True), ("second.csv", False)]


def test_discover_sample_data_specs_dedupes_entries(tmp_path):
    figures = tmp_path / "figures"
    figures.mkdir()
    frontmatter = """---
sample_data:
  - filename: data.h5
    with_video: true
---
"""
    (figures / "one.qmd").write_text(frontmatter, encoding="utf-8")
    (figures / "two.qmd").write_text(frontmatter, encoding="utf-8")

    assert discover_sample_data_specs(figures) == [("data.h5", True)]


def test_prefetch_sample_data_fetches_declared_datasets(monkeypatch, tmp_path):
    figures = tmp_path / "figures"
    figures.mkdir()
    (figures / "one.qmd").write_text(
        """---
sample_data:
  - filename: data.h5
    with_video: true
---
""",
        encoding="utf-8",
    )

    calls: list[tuple[str, bool]] = []
    monkeypatch.setattr(
        "movement.sample_data.fetch_dataset",
        lambda filename, with_video=False: calls.append((filename, with_video)),
    )

    assert prefetch_sample_data(figures) == [("data.h5", True)]
    assert calls == [("data.h5", True)]
