"""The facts, the colours and the pictures that every graphic is made from.

A README graphic cannot load a font, so each word or sentence in the site's typeface,
Bricolage Grotesque, is kept as a white-on-black picture (pictures/words/) and used as a
mask over a field of colour. The 3D figure is the one the portfolio site draws; its still
frames are in pictures/guide-*/. The pages in capture/ made all of them.

Reading the facts needs nothing. Drawing needs Pillow.
"""
from __future__ import annotations

import base64
import io
import json
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # the facts below can still be read; build.py says what is missing
    Image = None

PICTURES = Path(__file__).resolve().parent / "pictures"

# The address of the portfolio site. The header and the "Open the site" button lead there.
# If this is ever emptied, the button is not built and the README must not link to it.
SITE = "https://hamdanesmail.vercel.app"

# name, field colour, ink colour, live address, and one sentence cut down from its repository's description
WORLDS = [
    ("Falaj", "#191410", "#ffffff", "https://falaj.falaj.workers.dev/",
     "UAEU's public website as ten MCP tools, read live with TinyFish."),
    ("Backed", "#ff7a1f", "#051016", "https://backed.hamdanesmail12-7a9.workers.dev/",
     "Who funded companies like yours, with the proof."),
    ("Standing", "#306a57", "#ffffff", "https://standing.hamdanesmail12-7a9.workers.dev/",
     "What the official register says about a person or a business, right now, with the proof."),
    ("Fineprint", "#f2eee3", "#1b1712", "https://fineprint.hamdanesmail12-7a9.workers.dev/",
     "A dated record of the web's small print: pricing pages, terms, policies and fee tables."),
    ("Redtape", "#c6162d", "#ffffff", "https://redtape.hamdanesmail12-7a9.workers.dev/",
     "Every licence, permit and filing to start one activity in three places, each fee proved on its official page or left open."),
    ("Groundwork", "#344d6e", "#ffffff", "https://groundwork.hamdanesmail12-7a9.workers.dev/",
     "Nine public records on one Philadelphia address, each linked to its source."),
    ("Upstream", "#fbfaf6", "#0c0a08", "https://upstream.hamdanesmail12-7a9.workers.dev/",
     "Highlight a claim on any page and follow it back to where it first appeared."),
    ("Knock", "#242e4a", "#ffffff", "https://knock.hamdanesmail12-7a9.workers.dev/",
     "Hand in a spreadsheet of companies and get it back with a verdict on every row, the day each was last seen and links to the evidence."),
    ("Takehome", "#e8e4d9", "#0c0a08", "https://takehome.hamdanesmail12-7a9.workers.dev/",
     "Take everything out of a student portal that has no export button."),
]
N = len(WORLDS)
HOLD, WIPE = 2.6, 0.9          # seconds each world rests in the header, and the curtain between two
STEP = HOLD + WIPE
TOTAL = STEP * N
GOLD, GOLD_INK = "#c9a45a", "#0c0a08"


# ---------------------------------------------------------------- words
def b64(data: bytes, kind: str) -> str:
    return f"data:image/{kind};base64," + base64.b64encode(data).decode()


_type = json.loads((PICTURES / "words" / "targets.json").read_text(encoding="utf-8"))
_dpr = _type["dpr"]
_words = {t["id"]: t for t in _type["targets"]}


def word(wid: str) -> dict:
    """A word in the site's typeface: a white-on-black picture, with where its ink and baseline are."""
    t = _words[wid]
    if "uri" not in t:
        im = Image.open(PICTURES / "words" / f"{wid}.png").convert("L")
        box = im.point(lambda v: 255 if v > 10 else 0).getbbox()
        t["l"], t["r"] = box[0] / _dpr, box[2] / _dpr
        # Names keep their full size; sentences are stored at the size a sharp screen shows them.
        shrink = 1.0 if wid in ("hamdan", "esmail") or wid.startswith("w-") else 0.5 if wid[:2] in ("b-", "j-", "s-") else 0.72
        if shrink != 1.0:
            im = im.resize((round(im.width * shrink), round(im.height * shrink)), Image.LANCZOS)
        buf = io.BytesIO()
        im.quantize(16).save(buf, "PNG", optimize=True)
        t["uri"] = b64(buf.getvalue(), "png")
    return t


def place(wid: str, size: float, x: float, y: float, anchor: str = "l") -> tuple[float, float, float, float]:
    """The box the word's picture takes when its ink starts (or ends) at x and its letters sit on y."""
    t = word(wid)
    k = size / t["em"]
    left = x - (t["l"] if anchor == "l" else t["r"]) * k
    return round(left, 2), round(y - t["base"] * k, 2), round(t["w"] * k, 2), round(t["h"] * k, 2)


def ink_width(wid: str, size: float) -> float:
    t = word(wid)
    return (t["r"] - t["l"]) * size / t["em"]


def mask(mid: str, wid: str, box: tuple) -> str:
    x, y, w, h = box
    return (f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="{x}" y="{y}" width="{w}" height="{h}">'
            f'<image href="{word(wid)["uri"]}" x="{x}" y="{y}" width="{w}" height="{h}"/></mask>')


def inked(mid: str, box: tuple, fill: str) -> str:
    x, y, w, h = box
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" mask="url(#{mid})"/>'


# ---------------------------------------------------------------- screenshots
def shot(name: str, width: int, quality: int = 72) -> str:
    im = Image.open(PICTURES / "shots" / f"{name.lower()}.webp").convert("RGB")
    if width < im.width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=quality, method=6)
    return b64(buf.getvalue(), "webp")


# ---------------------------------------------------------------- the 3D figure
HEADER_FRAMES = ["idle", "talk3", "talk6", "air", "wave1", "wave2"]


def header_frames() -> tuple[dict, tuple]:
    """The frames the header uses, all cut to one shared box (in the page's own pixels)."""
    ims = {f: Image.open(PICTURES / "guide-header" / f"{f}.png").convert("RGBA") for f in HEADER_FRAMES}
    l, t, r, b = 10 ** 6, 10 ** 6, 0, 0
    for im in ims.values():
        x0, y0, x1, y1 = im.getbbox()
        l, t, r, b = min(l, x0), min(t, y0), max(r, x1), max(b, y1)
    l, t, r, b = max(0, l - 2), max(0, t - 2), r + 2, b + 2
    out = {}
    for f, im in ims.items():
        buf = io.BytesIO()
        im.crop((l, t, r, b)).quantize(colors=96, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE).save(buf, "PNG", optimize=True)
        out[f] = b64(buf.getvalue(), "png")
    return out, (l / 2, t / 2, (r - l) / 2, (b - t) / 2)


def terminal_frames() -> tuple[dict, tuple, int]:
    """The figure as outlines, in four build stages, turning once, and waving, all cut to one shared box."""
    meta = json.loads((PICTURES / "guide-terminal" / "targets.json").read_text(encoding="utf-8"))
    k = meta["dpr"]
    ims = {t["id"]: Image.open(PICTURES / "guide-terminal" / f"{t['id']}.png").convert("RGBA") for t in meta["targets"]}
    l, t, r, b = 10 ** 6, 10 ** 6, 0, 0
    for im in ims.values():
        x0, y0, x1, y1 = im.getbbox()
        l, t, r, b = min(l, x0), min(t, y0), max(r, x1), max(b, y1)
    l, t, r, b = max(0, l - 2), max(0, t - 2), r + 2, b + 2
    out = {}
    for f, im in ims.items():
        buf = io.BytesIO()
        im.crop((l, t, r, b)).quantize(colors=64, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE).save(buf, "PNG", optimize=True)
        out[f] = b64(buf.getvalue(), "png")
    return out, (l / k, t / k, (r - l) / k, (b - t) / k), meta["targets"][0]["boxes"]


FRAME_H, FEET, MID, POSE_DPR = 488, 473, 225, 2      # the capture frame of guide-poses.html, in its own pixels


def poses(ids: list, unit_h: float, colors: int = 64) -> tuple[dict, tuple]:
    """Poses of the figure, cut to one shared box and sized for a figure drawn `unit_h` units tall (whole frame)."""
    k = unit_h / FRAME_H
    ims = {f: Image.open(PICTURES / "guide-poses" / f"{f}.png").convert("RGBA") for f in ids}
    l, t, r, b = 10 ** 6, 10 ** 6, 0, 0
    for im in ims.values():
        x0, y0, x1, y1 = im.getbbox()
        l, t, r, b = min(l, x0), min(t, y0), max(r, x1), max(b, y1)
    l, t = max(0, l - 2), max(0, t - 2)
    r, b = min(r + 2, 900), min(b + 2, 976)
    box = (l / POSE_DPR * k, t / POSE_DPR * k, (r - l) / POSE_DPR * k, (b - t) / POSE_DPR * k)
    px = (max(8, round(box[2] * 1.5)), max(8, round(box[3] * 1.5)))
    out = {}
    for f, im in ims.items():
        small = im.crop((l, t, r, b)).convert("RGBa").resize(px, Image.LANCZOS).convert("RGBA")
        buf = io.BytesIO()
        small.quantize(colors=colors, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE).save(buf, "PNG", optimize=True)
        out[f] = b64(buf.getvalue(), "png")
    return out, box


# ---------------------------------------------------------------- the sheet itself
def svg(w: int, h: int, body: str, title: str, style: str = "") -> str:
    css = f"<style>{style}</style>" if style else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">'
            f"<title>{title}</title>{css}{body}</svg>")


def squares(x: float, y: float, on: int, fill: str, size: int = 9, gap: int = 7) -> str:
    """Nine small squares, one per world, with this world's square solid."""
    return "".join(
        f'<rect x="{x + n * (size + gap)}" y="{y}" width="{size}" height="{size}" fill="{fill}"'
        f'{"" if n == on else " opacity=\".28\""}/>' for n in range(N))
