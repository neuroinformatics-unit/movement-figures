"""Copy the graphic assets used by the scenes into ``assets/``.

The sources live in the NIU shared Dropbox and are not committed, as some
are third-party logos. Override the location with ``MOVEMENT_RESOURCES``.
"""

import os
import subprocess
from pathlib import Path

from PIL import Image

RESOURCES = Path(
    os.environ.get(
        "MOVEMENT_RESOURCES",
        Path.home() / "UCL Dropbox/Nikoloz Sirmpilatze/NIU/resources",
    )
)
SOURCES = [
    "logos/movement/movement_logo_on-transparent.png",
    "figures/movement/DLC_logo.png",
    "figures/movement/SLEAP_logo.png",
    "figures/movement/LightningPose_logo.png",
    "figures/movement/NWB_logo.png",
    "figures/movement/netcdf_icon.png",
]
# Vector logos, rasterised with Inkscape
SVG_SOURCES = ["figures/scipy_ecosystem/logos/python-logo-generic.svg"]



def save_trimmed(src, out):
    """RGBA, trimmed to the visible content, so logos size consistently."""
    img = Image.open(src).convert("RGBA")
    img.crop(img.getchannel("A").getbbox()).save(out)


dest = Path(__file__).resolve().parent / "assets"
dest.mkdir(exist_ok=True)
for rel in SOURCES:
    save_trimmed(RESOURCES / rel, dest / Path(rel).name)
    print(f"copied {rel}")
for rel in SVG_SOURCES:
    out = dest / Path(rel).with_suffix(".png").name
    subprocess.run(
        ["inkscape", str(RESOURCES / rel), "--export-height=600", "-o", str(out)],
        check=True,
        capture_output=True,
    )
    save_trimmed(out, out)
    print(f"rasterised {rel}")
