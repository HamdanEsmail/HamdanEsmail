"""Checks that every generated graphic is something GitHub will actually render.

Run from the repository root with:  python -m pytest -q
"""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "assets" / "src"))

import build  # noqa: E402

EXPECTED = ["header", "tag-now", "featured", "project-keepers-lantern", "project-firstrole",
            "project-coursesignal", "project-study-sprint", "toolkit", "tag-education", "tag-contact", "hello"]


def setup_module(module):
    build.build()


def svg_files():
    return sorted((ROOT / "assets").glob("*.svg"))


def test_every_graphic_has_a_light_and_a_dark_variant():
    names = {p.name for p in svg_files()}
    for base in EXPECTED:
        assert f"{base}-light.svg" in names
        assert f"{base}-dark.svg" in names


def test_svgs_are_well_formed_xml():
    for path in svg_files():
        ET.fromstring(path.read_text(encoding="utf-8"))


def test_svgs_load_nothing_from_the_network_and_run_no_scripts():
    for path in svg_files():
        text = path.read_text(encoding="utf-8")
        assert "<script" not in text, path.name
        assert "@import" not in text, path.name
        hrefs = re.findall(r'href="([^"]+)"', text)
        for h in hrefs:
            assert h.startswith("data:image/"), f"{path.name} references {h[:40]}"
        assert "http" not in text.replace("http://www.w3.org/2000/svg", ""), path.name


def test_svgs_stay_small_enough_for_a_readme():
    for path in svg_files():
        assert path.stat().st_size < 400_000, f"{path.name} is {path.stat().st_size} bytes"


def test_readme_references_only_assets_that_exist():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    refs = set(re.findall(r'(?:src|srcset)="(assets/[^"]+)"', readme))
    assert refs, "README references no assets"
    for ref in refs:
        assert (ROOT / ref).exists(), ref
    for base in EXPECTED:
        assert f"assets/{base}-light.svg" in refs
        assert f"assets/{base}-dark.svg" in refs


def test_featured_numbers_match_the_dubai_facts():
    text = (ROOT / "assets" / "featured-light.svg").read_text(encoding="utf-8")
    for value in build.DUBAI.values():
        assert value in text
