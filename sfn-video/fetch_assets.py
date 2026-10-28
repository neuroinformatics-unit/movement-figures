"""Copy the graphic assets used by the scenes into ``assets/``.

The sources live in the NIU shared Dropbox and are not committed, as some
are third-party logos. Override the location with ``MOVEMENT_RESOURCES``.
"""

import os
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

dest = Path(__file__).resolve().parent / "assets"
dest.mkdir(exist_ok=True)
for rel in SOURCES:
    # RGBA, trimmed to the visible content, so logos size consistently
    img = Image.open(RESOURCES / rel).convert("RGBA")
    img.crop(img.getchannel("A").getbbox()).save(dest / Path(rel).name)
    print(f"copied {rel}")
