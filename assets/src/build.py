"""Build the profile README graphics.

Run from the repository root:

    python assets/src/build.py

Writes every SVG the README shows into assets/. Needs Pillow (pip install pillow).

Everything GitHub needs from an SVG it shows through <img> is respected here: no scripts,
no outside fonts or files, and only animation that lives inside the file. With motion turned
off, or where animation is not supported, each graphic shows a finished still.

    pieces.py     the facts, the colours and the pictures (words as masks, frames of the 3D figure)
    header.py     the header that plays the portfolio site by itself, and the gold buttons
    terminal.py   the terminal that draws the figure, then says who he is
    panels.py     About, How I got here, and one band per world
    pictures/     what the graphics are cut from
    capture/      the pages that made those pictures (needs Node, Chrome and the site's own code)
"""
from __future__ import annotations

from pathlib import Path

import header
import panels
import pieces
import terminal

ASSETS = Path(__file__).resolve().parents[1]


def graphics() -> dict[str, str]:
    """Every graphic, by the name of its file."""
    if pieces.Image is None:
        raise SystemExit("The build needs Pillow:  pip install pillow")
    made = {"header": header.header(), "terminal": terminal.terminal(), "about": panels.about(), "journey": panels.journey()}
    for i, world in enumerate(pieces.WORLDS):
        made[f"world-{world[0].lower()}"] = panels.band(i)
    made["hello"] = header.button("t-say-hello", "Say hello")
    if pieces.SITE:
        made["open"] = header.button("t-open-site", "Open the site")
    return made


def build() -> None:
    made = graphics()
    for name, text in made.items():
        (ASSETS / f"{name}.svg").write_text(text, encoding="utf-8", newline="\n")
        print(f"{name + '.svg':24}{len(text.encode()) / 1024:6.0f} KB")
    print(f"{'all together':24}{sum(len(t.encode()) for t in made.values()) / 1024:6.0f} KB")


if __name__ == "__main__":
    build()
