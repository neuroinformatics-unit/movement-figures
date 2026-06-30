"""Consistent vector export for figures."""

from collections.abc import Generator, Sequence
from contextlib import contextmanager
from pathlib import Path

import matplotlib as mpl
from matplotlib.figure import Figure

# Per-backend metadata keys to suppress the wall-clock render timestamp.
# SVG uses "Date"; PDF uses "CreationDate". Setting them to None omits the
# field entirely, making outputs byte-deterministic for reproducible diffs.
_TIMESTAMP_SUPPRESS: dict[str, dict[str, None]] = {
    "svg": {"Date": None},
    "pdf": {"CreationDate": None},
}

# Fixed salt for the SVG renderer's path ID hash.  When svg.hashsalt is None
# matplotlib falls back to uuid.uuid4(), which differs on every render.
_SVG_HASHSALT = "movement-figures"


def _default_output_dir() -> Path:
    """Return ``<project-root>/outputs``, found by walking up to ``pyproject.toml``.

    This keeps ``save_figure`` writing to the same place whether it runs under
    ``quarto render`` (cwd = project root) or interactively from a figure's own
    directory (cwd = ``figures/``). Falls back to ``./outputs`` if no marker is
    found.
    """
    here = Path.cwd().resolve()
    for parent in (here, *here.parents):
        if (parent / "pyproject.toml").is_file():
            return parent / "outputs"
    return here / "outputs"


@contextmanager
def _deterministic_svg_context() -> Generator[None, None, None]:
    """Temporarily pin svg.hashsalt so path IDs are stable across renders."""
    with mpl.rc_context({"svg.hashsalt": _SVG_HASHSALT}):
        yield


def save_figure(
    fig: Figure,
    name: str,
    formats: Sequence[str] = ("pdf",),
    output_dir: str | Path | None = None,
) -> list[Path]:
    """Save ``fig`` as vector files named ``<name>.<fmt>`` in ``output_dir``.

    Returns the list of written paths. Creates ``output_dir`` if absent. When
    ``output_dir`` is ``None`` (the default), writes to ``<project-root>/outputs``
    regardless of the current working directory, so the path is the same under
    ``quarto render`` and interactive execution.

    Outputs are written without an embedded wall-clock timestamp and with a
    fixed SVG hash salt so that re-rendering the same figure produces
    byte-identical files, enabling clean git diffs on committed vector outputs.
    """
    output_dir = _default_output_dir() if output_dir is None else Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for fmt in formats:
        path = output_dir / f"{name}.{fmt}"
        metadata = _TIMESTAMP_SUPPRESS.get(fmt.lower(), {})
        if fmt.lower() == "svg":
            with _deterministic_svg_context():
                fig.savefig(path, metadata=metadata)
        else:
            fig.savefig(path, metadata=metadata)

        paths.append(path)
    return paths
