"""The ``movement-video`` command: check inputs, update hashes, render."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from movement_figures.video.project import OK, RESOLUTIONS, Video, update_hashes


def _report(video: Video) -> bool:
    """Print the inputs' status; return whether all are as recorded."""
    sources = {item.file: item.source for item in video.inputs}
    status = video.check_inputs()
    for file, state in status.items():
        print(f"{state:>9}  {file}")
        if state != OK and file in sources:
            print(f"{'':>11}source: {sources[file]}")
    return all(state == OK for state in status.values())


def check(video: Video) -> int:
    if _report(video):
        print(f"All {len(video.inputs)} inputs match video.yml")
        return 0
    print(
        f"\nPut missing files in {video.inputs_dir}; after adding or replacing "
        "one on purpose, run `movement-video update-hashes`."
    )
    return 1


def render(video: Video, resolution: str, modules: list[str] | None) -> int:
    if check(video):
        return 1
    if modules:
        unknown = set(modules) - {s.module for s in video.segments}
        if unknown:
            print(f"No such segment: {', '.join(sorted(unknown))}")
            return 1
    segments = [s for s in video.segments if not modules or s.module in modules]

    from movement import sample_data

    for filename, with_video in video.sample_data:
        sample_data.fetch_dataset(filename, with_video=with_video)

    flags = RESOLUTIONS[resolution][0]
    for segment in segments:
        subprocess.run(
            [sys.executable, "-m", "manim", *flags]
            + ["--media_dir", str(video.media_dir)]
            + [f"{segment.module}.py", segment.scene],
            cwd=video.scenes_dir,
            check=True,
        )
    if modules:
        return 0

    # Each segment starts on the frame the previous one ends on, so the joins
    # need no re-encoding
    concat = video.media_dir / f"concat_{resolution}.txt"
    concat.write_text(
        "".join(f"file '{video.segment_path(s, resolution)}'\n" for s in segments)
    )
    out = video.output_path(resolution)
    subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0"]
        + ["-i", str(concat), "-c", "copy", str(out)],
        check=True,
    )
    print(f"Wrote {out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="movement-video", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    p = commands.add_parser("check", help="check inputs/ against video.yml")
    p.add_argument("video", type=Path, help="video folder, e.g. videos/showcase")

    p = commands.add_parser("update-hashes", help="record the inputs' hashes")
    p.add_argument("video", type=Path)
    p.add_argument("files", nargs="*", help="only these inputs (default: all)")

    p = commands.add_parser("render", help="render and join all segments")
    p.add_argument("video", type=Path)
    p.add_argument("--resolution", choices=RESOLUTIONS, default="720p")
    p.add_argument(
        "--segment",
        dest="segments",
        action="append",
        metavar="MODULE",
        help="render only this segment, without joining (repeatable)",
    )

    args = parser.parse_args(argv)
    try:
        video = Video.load(args.video)
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    if args.command == "check":
        return check(video)
    if args.command == "update-hashes":
        updated = update_hashes(video, args.files or None)
        print(f"Updated {len(updated)} hashes: {', '.join(updated) or '-'}")
        return 0
    return render(video, args.resolution, args.segments)


if __name__ == "__main__":
    raise SystemExit(main())
