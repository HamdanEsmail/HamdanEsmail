"""Checks that every graphic the README shows is something GitHub will actually render.

Run from the repository root with:  python -m pytest -q

These tests read the graphics that are committed. They never write into assets/: the build
uses Pillow, whose picture bytes differ a little from one version to the next, so a test run
must not replace graphics that have already been looked at.
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
sys.path.insert(0, str(ASSETS / "src"))

import pieces  # noqa: E402

WORLDS = [w[0].lower() for w in pieces.WORLDS]
EXPECTED = (["header", "terminal", "about", "journey"] + [f"world-{w}" for w in WORLDS] + ["hello"]
            + (["open"] if pieces.SITE else []))
SVG = "http://www.w3.org/2000/svg"
PICTURE = re.compile(r'data:[^"]+')


def text_of(name: str) -> str:
    return (ASSETS / f"{name}.svg").read_text(encoding="utf-8")


def readme() -> str:
    """The README with every run of spaces and line breaks read as one space, as a browser reads a tag."""
    return re.sub(r"\s+", " ", (ROOT / "README.md").read_text(encoding="utf-8"))


def test_the_graphics_are_exactly_the_ones_the_build_makes():
    assert sorted(p.stem for p in ASSETS.glob("*.svg")) == sorted(EXPECTED)


@pytest.mark.parametrize("name", EXPECTED)
def test_svg_is_well_formed_xml(name):
    root = ET.fromstring(text_of(name))
    assert root.tag == f"{{{SVG}}}svg"
    assert root.find(f"{{{SVG}}}title").text, "a graphic with no title says nothing to a screen reader"


@pytest.mark.parametrize("name", EXPECTED)
def test_svg_loads_nothing_from_the_network_and_runs_no_scripts(name):
    text = text_of(name)
    assert "<script" not in text
    assert "@import" not in text
    for href in re.findall(r'href="([^"]+)"', text):
        assert href.startswith("data:image/"), f"references {href[:40]}"
    # Embedded pictures are long runs of letters that can spell anything, so they are left out of this search.
    assert "http" not in PICTURE.sub("", text).replace(SVG, "")


@pytest.mark.parametrize("name", EXPECTED)
def test_svg_shows_a_finished_still_when_motion_is_off(name):
    text = text_of(name)
    if "animation:" in text or "<animate" in text:
        assert "prefers-reduced-motion:reduce" in text


def test_svgs_stay_small_enough_for_a_readme():
    sizes = {name: (ASSETS / f"{name}.svg").stat().st_size for name in EXPECTED}
    for name, size in sizes.items():
        assert size < 400_000, f"{name} is {size} bytes"
    assert sum(sizes.values()) < 2_500_000, f"all together: {sum(sizes.values())} bytes"


def test_readme_uses_every_graphic_and_nothing_that_is_missing():
    refs = set(re.findall(r'(?:src|srcset)="(assets/[^"]+)"', readme()))
    assert refs == {f"assets/{name}.svg" for name in EXPECTED}


def test_the_stacked_pictures_touch():
    # A space or a line break between two pictures of a stack would show as a gap on GitHub.
    stacks = re.findall(r"<p>(.*?)</p>", readme(), flags=re.S)
    tall = [s for s in stacks if s.count('width="100%"') > 1]
    assert len(tall) == 2, "expected the About stack and the tower of worlds"
    for stack in tall:
        assert not re.search(r">\s+<", stack)
        assert stack.count('align="top"') == stack.count("<img")


@pytest.mark.parametrize("world", pieces.WORLDS, ids=WORLDS)
def test_each_world_is_a_band_that_opens_the_live_build(world):
    name, _field, _ink, live, line = world
    band = f'<a href="{live}"><img src="assets/world-{name.lower()}.svg" width="100%" align="top" alt="{name}. {line}"></a>'
    assert band in readme()
    # The same sentence, as real text, with the way to the code.
    assert f"<b>{name}.</b> {line}" in readme()
    assert f'href="https://github.com/HamdanEsmail/{name.lower()}"' in readme()
    assert line in ET.fromstring(text_of(f"world-{name.lower()}")).find(f"{{{SVG}}}title").text
    # And the sentence drawn inside the band is that sentence too.
    drawn = json.loads((ASSETS / "src" / "pictures" / "words" / "targets.json").read_text(encoding="utf-8"))["targets"]
    assert {t["id"]: t["text"] for t in drawn}[f"s-{name.lower()}"] == line


def test_the_build_still_draws_what_is_committed():
    """Rebuild in memory and compare everything except the embedded pictures."""
    pytest.importorskip("PIL")
    import build

    fresh = build.graphics()
    assert sorted(fresh) == sorted(EXPECTED)
    for name, text in fresh.items():
        assert PICTURE.sub("", text) == PICTURE.sub("", text_of(name)), f"{name}.svg is out of date: run python assets/src/build.py"
