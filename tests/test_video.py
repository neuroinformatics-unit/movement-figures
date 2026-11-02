from datetime import date

import pytest

from movement_figures.video import cli
from movement_figures.video.project import (
    CHANGED,
    MISSING,
    OK,
    UNHASHED,
    UNLISTED,
    Segment,
    Video,
    sha256,
    update_hashes,
)

VIDEO_YML = """\
# a comment that must survive update-hashes
name: demo
segments:
  - module: s01_intro
    scene: Intro
sample_data:
  - filename: data.h5
    with_video: true
inputs:
  - file: logo.png
    source: somewhere  # where to get it
    sha256:
  - file: clip.mp4
    source: elsewhere
    credit: Someone
    sha256:
"""


@pytest.fixture
def project(tmp_path):
    (tmp_path / "video.yml").write_text(VIDEO_YML, encoding="utf-8")
    inputs = tmp_path / "inputs"
    inputs.mkdir()
    (inputs / "logo.png").write_bytes(b"logo")
    (inputs / "clip.mp4").write_bytes(b"clip")
    return tmp_path


def test_load_reads_video_yml(project):
    video = Video.load(project)
    assert video.name == "demo"
    assert video.segments == (Segment("s01_intro", "Intro"),)
    assert video.sample_data == (("data.h5", True),)
    assert [i.file for i in video.inputs] == ["logo.png", "clip.mp4"]
    assert video.inputs[1].credit == "Someone"


def test_load_requires_a_sha256_key(project):
    yml = project / "video.yml"
    yml.write_text(VIDEO_YML.replace("    credit: Someone\n    sha256:\n", ""))
    with pytest.raises(ValueError, match="missing 'sha256'"):
        Video.load(project)


def test_load_reports_malformed_entries(project, capsys):
    yml = project / "video.yml"
    # Without the `inputs:` key, the inputs would read as sample data
    yml.write_text(VIDEO_YML.replace("inputs:\n", ""))
    with pytest.raises(ValueError, match="sample_data entry 2.*missing 'filename'"):
        Video.load(project)
    assert cli.main(["check", str(project)]) == 1
    assert "missing 'filename'" in capsys.readouterr().err


def test_update_hashes_records_hashes_and_keeps_comments(project):
    updated = update_hashes(Video.load(project))
    assert updated == ["logo.png", "clip.mp4"]
    text = (project / "video.yml").read_text()
    assert "# a comment that must survive update-hashes" in text
    assert "source: somewhere  # where to get it" in text
    video = Video.load(project)
    assert video.inputs[0].sha256 == sha256(project / "inputs" / "logo.png")
    assert update_hashes(video) == []


def test_update_hashes_only_named_files(project):
    assert update_hashes(Video.load(project), ["clip.mp4"]) == ["clip.mp4"]
    assert Video.load(project).inputs[0].sha256 is None


def test_update_hashes_rejects_unlisted_files(project):
    with pytest.raises(ValueError, match="other.png"):
        update_hashes(Video.load(project), ["other.png"])


def test_check_inputs_reports_each_state(project):
    assert set(Video.load(project).check_inputs().values()) == {UNHASHED}
    update_hashes(Video.load(project))
    inputs = project / "inputs"
    (inputs / "logo.png").write_bytes(b"new logo")
    (inputs / "clip.mp4").unlink()
    (inputs / "extra.txt").write_text("not listed")
    assert Video.load(project).check_inputs() == {
        "logo.png": CHANGED,
        "clip.mp4": MISSING,
        "extra.txt": UNLISTED,
    }


def test_output_and_segment_paths(project):
    video = Video.load(project)
    assert video.output_path("1080p", date(2026, 11, 2)) == (
        project / "media" / "demo_2026-11-02_1080p.mp4"
    )
    assert video.segment_path(video.segments[0], "720p") == (
        project / "media" / "videos" / "s01_intro" / "720p30" / "Intro.mp4"
    )


def test_cli_check_exit_codes(project, capsys):
    assert cli.main(["check", str(project)]) == 1
    assert cli.main(["update-hashes", str(project)]) == 0
    assert cli.main(["check", str(project)]) == 0
    assert f"{OK:>9}  logo.png" in capsys.readouterr().out


def test_render_stops_on_bad_inputs(project, monkeypatch):
    monkeypatch.setattr(
        cli.subprocess, "run", lambda *a, **k: pytest.fail("rendered anyway")
    )
    assert cli.main(["render", str(project)]) == 1


def test_brand_registers_fonts_and_image_fits_screen(tmp_path):
    pytest.importorskip("manim")
    import numpy as np
    from PIL import Image

    from movement_figures.video.brand import TEAL
    from movement_figures.video.elements import image, screen_pixels

    assert TEAL == "#66c2a5"
    logo = tmp_path / "logo.png"
    Image.fromarray(np.full((40, 80, 4), [0, 0, 0, 255], np.uint8)).save(logo)
    mob = image(logo, 1.0)
    assert mob.height == pytest.approx(1.0)
    assert mob.pixel_array.shape[0] == screen_pixels(1.0)
