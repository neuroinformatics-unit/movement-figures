"""Discover and prefetch movement sample data declared in figure frontmatter.

Figures fetch their datasets via ``movement.sample_data`` inside code cells.
The first fetch downloads the data, and ``pooch``'s progress bars leak into
Quarto's captured stdout, showing up as stray code-block outputs on the rendered
site. To avoid that, CI runs the ``prefetch-sample-data`` console script before
``quarto render``: this module reads each figure's ``sample_data:`` frontmatter
and downloads everything up front, in a step whose stdout is not captured, so the
render finds the data already cached and stays quiet.
"""

from __future__ import annotations

from pathlib import Path

import yaml


def _load_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    return yaml.safe_load(text[4:end]) or {}


def read_sample_data_specs(path: str | Path) -> list[tuple[str, bool]]:
    """Read (filename, with_video) sample-data declarations from a figure."""
    entries = _load_frontmatter(Path(path)).get("sample_data") or []
    return [(e["filename"], bool(e.get("with_video", False))) for e in entries]


def discover_sample_data_specs(
    figures_dir: str | Path = "figures",
) -> list[tuple[str, bool]]:
    """Collect unique sample-data declarations across figure documents."""
    seen: dict[tuple[str, bool], None] = {}
    for figure_path in sorted(Path(figures_dir).glob("*.qmd")):
        for spec in read_sample_data_specs(figure_path):
            seen.setdefault(spec, None)
    return list(seen)


def prefetch_sample_data(
    figures_dir: str | Path = "figures",
) -> list[tuple[str, bool]]:
    """Fetch every sample-data dataset declared by the gallery figures."""
    # Imported lazily so `movement-figures --help` doesn't trigger a download.
    from movement import sample_data

    specs = discover_sample_data_specs(figures_dir)
    for filename, with_video in specs:
        sample_data.fetch_dataset(filename, with_video=with_video)
    return specs


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(prog="prefetch-sample-data")
    parser.add_argument(
        "--figures-dir",
        default="figures",
        help="directory containing the figure .qmd files (default: ./figures)",
    )
    args = parser.parse_args(argv)
    specs = prefetch_sample_data(args.figures_dir)
    print(f"Prefetched {len(specs)} sample-data datasets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
