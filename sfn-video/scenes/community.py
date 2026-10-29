"""The contributors credited on movement's People page."""

import re
from pathlib import Path

PEOPLE = "https://movement.neuroinformatics.dev/dev/_sources/community/people.md.txt"
CACHE = Path(__file__).resolve().parent.parent / "cache" / "contributors.txt"


def contributors():
    """Contributor names (GitHub handles where no name is set), alphabetical.

    Downloaded once and cached; delete the cache to pick up newcomers.
    """
    if not CACHE.exists():
        from urllib.request import urlopen

        page = urlopen(PEOPLE).read().decode()
        names = {n.strip() for n in re.findall(r"<sub><b>(.*?)</b></sub>", page)}
        CACHE.parent.mkdir(exist_ok=True)
        CACHE.write_text("\n".join(sorted(names, key=str.casefold)) + "\n")
    return CACHE.read_text().splitlines()
