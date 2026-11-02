"""A video project: a folder of manim scenes described by a ``video.yml``.

The folder holds::

    video.yml   output name, segments, sample data, and the inputs manifest
    scenes/     the manim modules, one scene per segment
    assets/     small files committed to the repo
    inputs/     files that can't be committed, populated by hand
    media/      renders (not committed)

Every file in ``inputs/`` has a manifest entry recording where to get it and
the sha256 of the version used, so a render can be checked against (and
reproduced from) the exact inputs of an earlier one.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml

# manim quality flags and the media subfolder each writes to
RESOLUTIONS: dict[str, tuple[tuple[str, ...], str]] = {
    "720p": (("-qm",), "720p30"),
    "1080p": (("-qh", "--fps", "30"), "1080p30"),  # the -qh preset is 60 fps
}

OK, MISSING, CHANGED, UNHASHED, UNLISTED = (
    "ok",
    "missing",
    "changed",
    "unhashed",
    "unlisted",
)


@dataclass(frozen=True)
class Segment:
    module: str
    scene: str


@dataclass(frozen=True)
class Input:
    """A file in ``inputs/``: where to get it, and the hash of the one used."""

    file: str
    source: str
    sha256: str | None = None
    credit: str | None = None


@dataclass(frozen=True)
class Video:
    root: Path
    name: str
    segments: tuple[Segment, ...]
    sample_data: tuple[tuple[str, bool], ...]
    inputs: tuple[Input, ...]

    @classmethod
    def load(cls, root: str | Path) -> Video:
        """Read ``<root>/video.yml``."""
        root = Path(root).resolve()
        spec = yaml.safe_load((root / "video.yml").read_text(encoding="utf-8"))
        inputs = []
        for entry in spec.get("inputs") or []:
            # update_hashes edits existing sha256 lines; it never adds them
            if "sha256" not in entry:
                raise ValueError(
                    f"input {entry['file']!r} has no sha256 key; "
                    "add an empty one (`sha256:`) for update-hashes to fill"
                )
            inputs.append(Input(**entry))
        return cls(
            root=root,
            name=spec["name"],
            segments=tuple(Segment(**s) for s in spec["segments"]),
            sample_data=tuple(
                (s["filename"], bool(s.get("with_video", False)))
                for s in spec.get("sample_data") or []
            ),
            inputs=tuple(inputs),
        )

    @property
    def scenes_dir(self) -> Path:
        return self.root / "scenes"

    @property
    def inputs_dir(self) -> Path:
        return self.root / "inputs"

    @property
    def media_dir(self) -> Path:
        return self.root / "media"

    def check_inputs(self) -> dict[str, str]:
        """Status of every listed input, plus any unlisted file in ``inputs/``."""
        status = {}
        for item in self.inputs:
            path = self.inputs_dir / item.file
            if not path.is_file():
                status[item.file] = MISSING
            elif not item.sha256:
                status[item.file] = UNHASHED
            elif sha256(path) != item.sha256:
                status[item.file] = CHANGED
            else:
                status[item.file] = OK
        if self.inputs_dir.is_dir():
            for path in sorted(self.inputs_dir.iterdir()):
                if path.is_file() and path.name not in status:
                    status[path.name] = UNLISTED
        return status

    def segment_path(self, segment: Segment, resolution: str) -> Path:
        """Where manim writes ``segment`` at ``resolution``."""
        subdir = RESOLUTIONS[resolution][1]
        return (
            self.media_dir / "videos" / segment.module / subdir / f"{segment.scene}.mp4"
        )

    def output_path(self, resolution: str, day: date | None = None) -> Path:
        """``media/<name>_<YYYY-MM-DD>_<resolution>.mp4``, dated by render day."""
        day = day or date.today()
        return self.media_dir / f"{self.name}_{day.isoformat()}_{resolution}.mp4"


def sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def update_hashes(video: Video, files: list[str] | None = None) -> list[str]:
    """Record the hashes of the inputs present (or only ``files``).

    ``video.yml`` is edited line by line, so its comments and layout survive.
    Returns the files whose recorded hash changed.
    """
    listed = {item.file for item in video.inputs}
    unknown = set(files or []) - listed
    if unknown:
        raise ValueError(f"not in the inputs manifest: {', '.join(sorted(unknown))}")
    path = video.root / "video.yml"
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    current, updated = None, []
    for i, line in enumerate(lines):
        if match := re.match(r"\s*-\s*file:\s*(.+?)\s*$", line):
            current = yaml.safe_load(match[1])
        elif current is not None and (match := re.match(r"(\s*sha256:)", line)):
            source = video.inputs_dir / current
            if (files is None or current in files) and source.is_file():
                new = f'{match[1]} "{sha256(source)}"\n'
                if line != new:
                    lines[i] = new
                    updated.append(current)
            current = None
    path.write_text("".join(lines), encoding="utf-8")
    return updated
