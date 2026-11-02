"""The contributors credited on movement's People page.

The list is committed, so a render doesn't depend on the live page; run this
module to refresh it when minting a new version.
"""

import re
from pathlib import Path

PEOPLE = "https://movement.neuroinformatics.dev/dev/_sources/community/people.md.txt"
CONTRIBUTORS = Path(__file__).resolve().parent.parent / "contributors.txt"


def contributors():
    """Contributor names (GitHub handles where no name is set), alphabetical."""
    return CONTRIBUTORS.read_text().splitlines()


def refresh():
    from urllib.request import urlopen

    page = urlopen(PEOPLE).read().decode()
    names = {n.strip() for n in re.findall(r"<sub><b>(.*?)</b></sub>", page)}
    CONTRIBUTORS.write_text("\n".join(sorted(names, key=str.casefold)) + "\n")


if __name__ == "__main__":
    refresh()
