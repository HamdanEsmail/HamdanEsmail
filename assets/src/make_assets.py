"""Generate every image in the profile README (modern geometric theme).

Weekly update: change CURRENT_WEEK and SHIPPED below, then run
    python assets/src/make_assets.py
It writes *.src.svg files here, then exports them with Inkscape
(text converted to paths) into assets/. Requires Inkscape on PATH or at
the default Windows install location.
"""
import math
import shutil
import subprocess
from pathlib import Path

# ---- weekly progress for Borrowed Alibi -------------------------------
CURRENT_WEEK = 0          # 0 = Prep Week 3, 1..12 = Weeks 1-12
SHIPPED = 0               # chapters shipped so far
WEEK_LABELS = ["P3"] + [f"W{i}" for i in range(1, 13)]

# ---- palette -----------------------------------------------------------
BG0, BG1, BG2 = "#0A1F22", "#0E2A2E", "#143A3E"
LINE = "#2B5A5C"
SAND, GOLD, TEAL, MUTED = "#E9DCC4", "#D4A84B", "#5FB3A8", "#9DB5B1"
CYAN = "#70CFCF"
SANS = 'font-family="Segoe UI"'
SEMI = 'font-family="Segoe UI Semibold"'

SRC = Path(__file__).parent
ASSETS = SRC.parent


# ---- geometry helpers ---------------------------------------------------
def star8_points(cx, cy, r, rot=0.0):
    """Eight-point star (two overlapping squares) as polygon points."""
    inner = r * math.cos(math.radians(45)) / math.cos(math.radians(22.5))
    pts = []
    for k in range(16):
        ang = math.radians(rot + k * 22.5 - 90)
        rad = r if k % 2 == 0 else inner
        pts.append(f"{cx + rad * math.cos(ang):.2f},{cy + rad * math.sin(ang):.2f}")
    return " ".join(pts)


def star8(cx, cy, r, rot=0.0, **attrs):
    a = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<polygon points="{star8_points(cx, cy, r, rot)}" {a}/>'


def defs_common():
    return f'''
    <pattern id="geo" width="56" height="56" patternUnits="userSpaceOnUse">
      {star8(28, 28, 17, fill="none", stroke=GOLD, stroke_width="0.9")}
      {star8(28, 28, 8, 22.5, fill="none", stroke=GOLD, stroke_width="0.6")}
      <polygon points="0,-6 6,0 0,6 -6,0" fill="none" stroke="{GOLD}" stroke-width="0.7"/>
      <polygon points="56,-6 62,0 56,6 50,0" fill="none" stroke="{GOLD}" stroke-width="0.7"/>
      <polygon points="0,50 6,56 0,62 -6,56" fill="none" stroke="{GOLD}" stroke-width="0.7"/>
      <polygon points="56,50 62,56 56,62 50,56" fill="none" stroke="{GOLD}" stroke-width="0.7"/>
      <line x1="11" y1="28" x2="0" y2="28" stroke="{GOLD}" stroke-width="0.6"/>
      <line x1="45" y1="28" x2="56" y2="28" stroke="{GOLD}" stroke-width="0.6"/>
      <line x1="28" y1="11" x2="28" y2="0" stroke="{GOLD}" stroke-width="0.6"/>
      <line x1="28" y1="45" x2="28" y2="56" stroke="{GOLD}" stroke-width="0.6"/>
    </pattern>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{BG1}"/><stop offset="1" stop-color="{BG0}"/>
    </linearGradient>
    <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{SAND}" stop-opacity="0"/>
      <stop offset="0.5" stop-color="{SAND}" stop-opacity="0.55"/>
      <stop offset="1" stop-color="{SAND}" stop-opacity="0"/>
    </linearGradient>'''


STYLE = '''
  <style>
    @keyframes spin { to { transform: rotate(360deg); } }
    @keyframes spinback { to { transform: rotate(-360deg); } }
    @keyframes sweep { 0% { transform: translateX(-300px); } 100% { transform: translateX(1700px); } }
    @keyframes pulse { 0%, 100% { opacity: 0.35; transform: scale(1); } 50% { opacity: 1; transform: scale(1.3); } }
    @keyframes travel { 0% { transform: translateX(0); opacity: 0; } 8% { opacity: 1; } 92% { opacity: 1; } 100% { transform: translateX(var(--d)); opacity: 0; } }
    .spin { transform-box: fill-box; transform-origin: center; animation: spin 160s linear infinite; }
    .spinback { transform-box: fill-box; transform-origin: center; animation: spinback 220s linear infinite; }
    .sweep { animation: sweep 9s ease-in-out infinite; }
    .pulse { transform-box: fill-box; transform-origin: center; animation: pulse 2.6s ease-in-out infinite; }
    @media (prefers-reduced-motion: reduce) {
      .spin, .spinback, .sweep, .pulse, .travel { animation: none !important; }
      .sweep, .travel { opacity: 0; }
    }
  </style>'''


def svg(w, h, body, extra_style=""):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{STYLE}{extra_style}
  <defs>{defs_common()}
  </defs>
{body}
</svg>
'''


def border_band(y, w, h=34):
    """A strip of small stars and diamonds with a moving gold shine."""
    items = []
    for i, x in enumerate(range(20, w, 40)):
        if i % 2 == 0:
            items.append(star8(x, y + h / 2, 7, fill="none", stroke=GOLD, stroke_width="1"))
        else:
            items.append(f'<polygon points="{x},{y + h / 2 - 5} {x + 5},{y + h / 2} {x},{y + h / 2 + 5} {x - 5},{y + h / 2}" fill="{GOLD}" opacity="0.6"/>')
    return f'''  <rect x="0" y="{y}" width="{w}" height="{h}" fill="{BG2}"/>
  <line x1="0" y1="{y}" x2="{w}" y2="{y}" stroke="{GOLD}" stroke-width="1.2" opacity="0.8"/>
  <line x1="0" y1="{y + h}" x2="{w}" y2="{y + h}" stroke="{GOLD}" stroke-width="1.2" opacity="0.8"/>
  <g opacity="0.85">{"".join(items)}</g>
  <rect class="sweep" x="0" y="{y}" width="260" height="{h}" fill="url(#shine)" opacity="0.35"/>'''


def rosette(cx, cy, scale=1.0, cls_outer="spin", cls_inner="spinback"):
    s = scale
    return f'''  <g>
    <circle cx="{cx}" cy="{cy}" r="{132 * s}" fill="{BG2}" opacity="0.55"/>
    <circle cx="{cx}" cy="{cy}" r="{126 * s}" fill="none" stroke="{GOLD}" stroke-width="1" opacity="0.5"/>
    <g class="{cls_outer}">
      {star8(cx, cy, 118 * s, fill="none", stroke=GOLD, stroke_width="1.6")}
      {star8(cx, cy, 118 * s, 22.5, fill="none", stroke=GOLD, stroke_width="0.9", opacity="0.6")}
    </g>
    <circle cx="{cx}" cy="{cy}" r="{78 * s}" fill="none" stroke="{TEAL}" stroke-width="1.2"/>
    <g class="{cls_inner}">
      {star8(cx, cy, 72 * s, fill=BG1, stroke=TEAL, stroke_width="1.4")}
      {star8(cx, cy, 72 * s, 22.5, fill="none", stroke=TEAL, stroke_width="0.8", opacity="0.7")}
    </g>
    {star8(cx, cy, 34 * s, fill=GOLD, opacity="0.95")}
    {star8(cx, cy, 16 * s, 22.5, fill=BG1)}
  </g>'''


# ---- 1. header ------------------------------------------------------------
def header():
    W, H = 1400, 420
    body = f'''  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#geo)" opacity="0.10"/>
  <radialGradient id="fade" cx="0.62" cy="0.45" r="0.5">
    <stop offset="0" stop-color="{BG1}" stop-opacity="0.95"/><stop offset="1" stop-color="{BG1}" stop-opacity="0"/>
  </radialGradient>
  <rect width="{W}" height="{H}" fill="url(#fade)"/>
{rosette(250, 190)}
  <text x="470" y="128" {SANS} font-size="34" fill="{GOLD}">حمدان</text>
  <text x="466" y="206" {SEMI} font-size="76" letter-spacing="2" fill="{SAND}">Hamdan Esmail</text>
  <text x="470" y="250" {SANS} font-size="18" letter-spacing="4.5" fill="{TEAL}">DATA SCIENCE &amp; ARTIFICIAL INTELLIGENCE  ·  UAEU</text>
  <line x1="470" y1="278" x2="1010" y2="278" stroke="{GOLD}" stroke-width="1.6"/>
  {star8(1024, 278, 9, fill=GOLD)}
  <text x="470" y="316" {SANS} font-size="15" letter-spacing="3" fill="{MUTED}">NOW BUILDING  BORROWED ALIBI  ·  HACK CLUB TERRA</text>
  {star8(1290, 70, 40, fill="none", stroke=GOLD, stroke_width="1", opacity="0.45")}
  {star8(1340, 150, 22, 22.5, fill="none", stroke=TEAL, stroke_width="1", opacity="0.45")}
{border_band(H - 44, W)}'''
    return svg(W, H, body)


# ---- 2. typing line --------------------------------------------------------
PHRASES = [
    "Data Science & AI student at UAEU",
    "Building tools students actually use",
    "Making a browser game, one chapter a week",
]


def typing(widths):
    W, H = 1400, 76
    n = len(PHRASES)
    period = 4 * n
    style = "\n  <style>\n"
    groups = []
    for i, phrase in enumerate(PHRASES):
        w = widths.get(f"p{i}", 600)
        chars = len(phrase)
        vis_end = 100 / n
        style += (f"    @keyframes vis{i} {{ 0% {{ opacity: 1; }} {vis_end - 0.5:.2f}% {{ opacity: 1; }} "
                  f"{vis_end:.2f}% {{ opacity: 0; }} 100% {{ opacity: 0; }} }}\n"
                  f"    @keyframes type{i} {{ 0% {{ transform: translateX(0); }} {vis_end * 0.55:.2f}% "
                  f"{{ transform: translateX({w + 6:.0f}px); }} 100% {{ transform: translateX({w + 6:.0f}px); }} }}\n"
                  f"    .g{i} {{ opacity: 0; animation: vis{i} {period}s linear {i * 4}s infinite; }}\n"
                  f"    .c{i} {{ animation: type{i} {period}s steps({chars}) {i * 4}s infinite; }}\n")
        groups.append(f'''  <g class="g{i}">
    <text id="p{i}" x="96" y="48" {SANS} font-size="26" fill="{SAND}">{phrase.replace("&", "&amp;")}</text>
    <g class="c{i}">
      <rect x="94" y="14" width="1260" height="50" fill="{BG1}"/>
      <rect class="blink" x="96" y="22" width="3" height="32" fill="{GOLD}"/>
    </g>
  </g>''')
    style += ("    @keyframes blink { 0%, 49% { opacity: 1; } 50%, 100% { opacity: 0; } }\n"
              "    .blink { animation: blink 1s steps(1) infinite; }\n"
              "    @media (prefers-reduced-motion: reduce) { .g0 { opacity: 1 !important; animation: none !important; }"
              " .g1, .g2 { animation: none !important; } .c0 { animation: none !important; transform: translateX(2000px); }"
              " .blink { animation: none !important; } }\n  </style>")
    body = f'''  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="38" fill="{BG1}" stroke="{LINE}" stroke-width="2"/>
  {star8(52, 38, 15, fill="none", stroke=GOLD, stroke_width="1.6")}
  {star8(52, 38, 6, fill=GOLD)}
{chr(10).join(groups)}'''
    return svg(W, H, body, style)


# ---- 3. project cards -------------------------------------------------------
def wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        if len(cur) + len(w_) + (1 if cur else 0) > width:
            lines.append(cur)
            cur = w_
        else:
            cur = f"{cur} {w_}" if cur else w_
    if cur:
        lines.append(cur)
    return lines


def icon(kind, cx, cy):
    if kind == "firstrole":
        return f'''<rect x="{cx - 34}" y="{cy - 44}" width="68" height="88" rx="6" fill="{SAND}"/>
      <rect x="{cx - 22}" y="{cy - 30}" width="44" height="5" rx="2" fill="{BG2}"/>
      <rect x="{cx - 22}" y="{cy - 16}" width="36" height="4" rx="2" fill="{MUTED}"/>
      <rect x="{cx - 22}" y="{cy - 6}" width="40" height="4" rx="2" fill="{MUTED}"/>
      <rect x="{cx - 22}" y="{cy + 4}" width="28" height="4" rx="2" fill="{MUTED}"/>
      <circle cx="{cx + 26}" cy="{cy + 34}" r="18" fill="{GOLD}"/>
      <path d="M {cx + 17},{cy + 34} l 6,6 l 11,-12" fill="none" stroke="{BG1}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'''
    if kind == "coursesignal":
        return f'''<path d="M {cx - 40},{cy - 30} h 64 a 12 12 0 0 1 12 12 v 34 a 12 12 0 0 1 -12 12 h -40 l -16 14 v -14 h -8 a 12 12 0 0 1 -12 -12 v -34 a 12 12 0 0 1 12 -12 z" fill="{SAND}"/>
      <circle cx="{cx - 18}" cy="{cy - 1}" r="4.5" fill="{BG2}"/><circle cx="{cx - 2}" cy="{cy - 1}" r="4.5" fill="{BG2}"/><circle cx="{cx + 14}" cy="{cy - 1}" r="4.5" fill="{BG2}"/>
      <path d="M {cx + 34},{cy - 46} a 22 22 0 0 1 16 16" fill="none" stroke="{GOLD}" stroke-width="3.5" stroke-linecap="round"/>
      <path d="M {cx + 36},{cy - 60} a 36 36 0 0 1 28 28" fill="none" stroke="{GOLD}" stroke-width="3.5" stroke-linecap="round" opacity="0.7"/>'''
    if kind == "studysprint":
        r = 40
        a = math.radians(-90 + 360 * 0.68)
        return f'''<circle cx="{cx}" cy="{cy + 4}" r="{r}" fill="none" stroke="{LINE}" stroke-width="9"/>
      <path d="M {cx},{cy + 4 - r} A {r} {r} 0 1 1 {cx + r * math.cos(a):.1f},{cy + 4 + r * math.sin(a):.1f}" fill="none" stroke="{GOLD}" stroke-width="9" stroke-linecap="round"/>
      <rect x="{cx - 8}" y="{cy - 50}" width="16" height="8" rx="2" fill="{SAND}"/>
      <line x1="{cx}" y1="{cy + 4}" x2="{cx}" y2="{cy - 18}" stroke="{SAND}" stroke-width="4" stroke-linecap="round"/>
      <line x1="{cx}" y1="{cy + 4}" x2="{cx + 14}" y2="{cy + 12}" stroke="{SAND}" stroke-width="4" stroke-linecap="round"/>
      <circle cx="{cx}" cy="{cy + 4}" r="4" fill="{GOLD}"/>'''
    # borrowed alibi: brass porthole with Echo's eye line
    return f'''<circle cx="{cx}" cy="{cy}" r="48" fill="#8C7A4E"/>
      <circle cx="{cx}" cy="{cy}" r="40" fill="#5E5236"/>
      <circle cx="{cx}" cy="{cy}" r="36" fill="#0B1620"/>
      <rect x="{cx - 20}" y="{cy - 4}" width="40" height="8" rx="4" fill="#101B24" stroke="{CYAN}" stroke-width="2.4"/>
      <ellipse cx="{cx - 10}" cy="{cy + 20}" rx="4" ry="2" fill="#C08A54"/>
      <rect x="{cx - 24}" y="{cy + 26}" width="48" height="1.6" fill="#2E5F66"/>'''


CARDS = [
    ("firstrole", "FirstRole", "LIVE DEMO",
     "A student job finder that reads public careers pages and turns them into a shortlist with sources, match reasons, and freshness, not invented openings.",
     ["TypeScript", "Cloudflare Workers", "TinyFish"]),
    ("coursesignal", "CourseSignal", "LIVE DEMO",
     "An evidence-first student copilot in iMessage. It finds and reads live public sources, then replies with a short, receipt-backed answer.",
     ["TypeScript", "TinyFish", "iMessage"]),
    ("borrowedalibi", "Borrowed Alibi", "IN PROGRESS",
     "A browser investigation thriller released one chapter a week. Walk the scene, compare a recorded memory with the room, and decide what goes on record.",
     ["Phaser 3", "JavaScript", "SVG art"]),
    ("studysprint", "Study Sprint", "HACK CLUB TERRA",
     "A local-first focus timer: pick one task, run a sprint, and keep your queue after a refresh.",
     ["JavaScript", "HTML / CSS"]),
]


def card(kind, title, status, desc, chips):
    W, H = 700, 300
    accent = CYAN if kind == "borrowedalibi" else GOLD
    lines = wrap(desc, 46)
    desc_svg = "".join(f'<text x="214" y="{126 + i * 25}" {SANS} font-size="17" fill="{MUTED}">{ln}</text>'
                       for i, ln in enumerate(lines))
    chip_svg, x = [], 214
    for c in chips:
        cw = 26 + len(c) * 8.1
        chip_svg.append(f'<rect x="{x}" y="{H - 62}" width="{cw:.0f}" height="30" rx="15" fill="none" stroke="{LINE}" stroke-width="1.6"/>'
                        f'<text x="{x + cw / 2:.1f}" y="{H - 41}" text-anchor="middle" {SANS} font-size="14" fill="{SAND}">{c}</text>')
        x += cw + 10
    sw = 24 + len(status) * 9.5
    body = f'''  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="url(#bg)" stroke="{LINE}" stroke-width="2"/>
  <clipPath id="tile"><rect x="34" y="34" width="150" height="{H - 68}" rx="16"/></clipPath>
  <rect x="34" y="34" width="150" height="{H - 68}" rx="16" fill="{BG2}"/>
  <rect x="34" y="34" width="150" height="{H - 68}" fill="url(#geo)" opacity="0.18" clip-path="url(#tile)"/>
  <g>
      {icon(kind, 109, H / 2)}
  </g>
  <text x="212" y="80" {SEMI} font-size="34" fill="{SAND}">{title}</text>
  <rect x="{W - 34 - sw:.0f}" y="52" width="{sw:.0f}" height="28" rx="14" fill="{accent}" opacity="0.16"/>
  <rect x="{W - 34 - sw:.0f}" y="52" width="{sw:.0f}" height="28" rx="14" fill="none" stroke="{accent}" stroke-width="1.4"/>
  <text x="{W - 34 - sw / 2:.1f}" y="71" text-anchor="middle" {SEMI} font-size="12.5" letter-spacing="1.5" fill="{accent}">{status}</text>
  {desc_svg}
  {"".join(chip_svg)}
  {star8(W - 40, H - 40, 10, fill="none", stroke=accent, stroke_width="1.2", opacity="0.7")}'''
    return svg(W, H, body)


# ---- 4. now building (Borrowed Alibi progress) -------------------------------
def now_building():
    W, H = 1400, 340
    x0, x1 = 660, 1336
    pts = []
    for i in range(13):
        t = i / 12
        pts.append((x0 + (x1 - x0) * t, 196 - 64 * math.sin(math.pi * t)))
    segs, nodes = [], []
    for i in range(12):
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        lit = i < SHIPPED
        segs.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{GOLD if lit else LINE}" '
                    f'stroke-width="{2 if lit else 1.4}" stroke-dasharray="{"none" if lit else "4 6"}"/>')
    for i, (x, y) in enumerate(pts):
        if i < SHIPPED:
            nodes.append(star8(x, y, 13, fill=GOLD))
            col = GOLD
        elif i == CURRENT_WEEK:
            nodes.append(f'<g class="pulse">{star8(x, y, 20, fill=CYAN, opacity="0.25")}</g>' + star8(x, y, 12, fill=CYAN))
            col = CYAN
        else:
            nodes.append(star8(x, y, 9, fill=BG1, stroke=MUTED, stroke_width="1.3", opacity="0.8"))
            col = MUTED
        nodes.append(f'<text x="{x:.1f}" y="{y + 38:.1f}" text-anchor="middle" {SANS} font-size="13" fill="{col}">{WEEK_LABELS[i]}</text>')
    week = "PREP WEEK 3" if CURRENT_WEEK == 0 else f"WEEK {CURRENT_WEEK}"
    body = f'''  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="24" fill="url(#bg)" stroke="{LINE}" stroke-width="2"/>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="24" fill="url(#geo)" opacity="0.07"/>
  <text x="64" y="84" {SEMI} font-size="15" letter-spacing="4" fill="{GOLD}">NOW BUILDING</text>
  <g class="pulse">{star8(232, 78, 7, fill=CYAN)}</g>
  <text x="62" y="150" {SEMI} font-size="56" fill="{SAND}">Borrowed Alibi</text>
  <text x="64" y="192" {SANS} font-size="19" fill="{MUTED}">An android investigation thriller for the browser.</text>
  <text x="64" y="220" {SANS} font-size="19" fill="{MUTED}">One new chapter every week for Hack Club Terra.</text>
  <text x="64" y="276" {SANS} font-size="14" letter-spacing="2.5" fill="{TEAL}">PHASER 3   ·   JAVASCRIPT   ·   SVG ART</text>
  <text x="{x0}" y="70" {SEMI} font-size="14" letter-spacing="3" fill="{CYAN}">{week}  ·  {SHIPPED} OF 13 CHAPTERS SHIPPED</text>
  {"".join(segs)}
  {"".join(nodes)}
  <text x="{x1}" y="300" text-anchor="end" {SANS} font-size="13" letter-spacing="2" fill="{MUTED}">OCT 2026  →  JAN 2027</text>'''
    return svg(W, H, body)


# ---- 5. journey timeline -------------------------------------------------------
JOURNEY = [
    ("UAEU", "B.Sc. Data Science & AI", "done"),
    ("FirstRole", "Sep 2026", "done"),
    ("CourseSignal", "Oct 2026", "done"),
    ("Study Sprint", "Oct 2026 · Terra prep", "done"),
    ("Borrowed Alibi", "Oct 2026 → Jan 2027", "now"),
    ("Next", "Internships & research", "next"),
]


def journey():
    W, H = 1400, 300
    y = 150
    xs = [110 + i * (1180 / (len(JOURNEY) - 1)) for i in range(len(JOURNEY))]
    now_i = next(i for i, j in enumerate(JOURNEY) if j[2] == "now")
    parts = [f'<line x1="{xs[0]}" y1="{y}" x2="{xs[now_i]}" y2="{y}" stroke="{GOLD}" stroke-width="2.4"/>',
             f'<line x1="{xs[now_i]}" y1="{y}" x2="{xs[-1]}" y2="{y}" stroke="{MUTED}" stroke-width="2" stroke-dasharray="6 8"/>']
    dist = xs[now_i] - xs[0]
    parts.append(f'<g class="travel" style="--d:{dist:.0f}px; animation: travel 7s ease-in-out infinite;">'
                 f'<circle cx="{xs[0]}" cy="{y}" r="5" fill="{SAND}"/></g>')
    for i, ((title, sub, state), x) in enumerate(zip(JOURNEY, xs)):
        above = i % 2 == 0
        ty = y - 56 if above else y + 62
        if state == "done":
            parts.append(star8(x, y, 16, fill=GOLD) + star8(x, y, 6, 22.5, fill=BG1))
            col = SAND
        elif state == "now":
            parts.append(f'<g class="pulse">{star8(x, y, 26, fill=CYAN, opacity="0.22")}</g>' + star8(x, y, 16, fill=CYAN))
            col = CYAN
        else:
            parts.append(star8(x, y, 15, fill=BG1, stroke=MUTED, stroke_width="1.6", stroke_dasharray="3 3"))
            col = MUTED
        parts.append(f'<text x="{x:.1f}" y="{ty}" text-anchor="middle" {SEMI} font-size="21" fill="{col}">{title}</text>'
                     f'<text x="{x:.1f}" y="{ty + 24}" text-anchor="middle" {SANS} font-size="14.5" fill="{MUTED}">{sub.replace("&", "&amp;")}</text>')
    body = f'''  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="24" fill="url(#bg)" stroke="{LINE}" stroke-width="2"/>
  <text x="44" y="46" {SEMI} font-size="14" letter-spacing="4" fill="{GOLD}">JOURNEY</text>
  {"".join(parts)}'''
    return svg(W, H, body)


# ---- 6. how I work + divider ---------------------------------------------------
def how_i_work():
    W, H = 1400, 250
    steps = [("Learn", "the concepts properly"), ("Build", "projects that actually run"), ("Apply", "to problems worth solving")]
    xs = [280, 700, 1120]
    cy = 104
    out = [f'<line x1="{xs[0]}" y1="{cy}" x2="{xs[-1]}" y2="{cy}" stroke="{GOLD}" stroke-width="1.6" opacity="0.7"/>']
    for (title, sub), x in zip(steps, xs):
        out.append(f'<circle cx="{x}" cy="{cy}" r="46" fill="{BG1}" stroke="{LINE}" stroke-width="2"/>'
                   + star8(x, cy, 36, fill="none", stroke=GOLD, stroke_width="1.6")
                   + star8(x, cy, 36, 22.5, fill="none", stroke=TEAL, stroke_width="1", opacity="0.7")
                   + star8(x, cy, 13, fill=GOLD)
                   + f'<text x="{x}" y="{cy + 86}" text-anchor="middle" {SEMI} font-size="24" fill="{SAND}">{title}</text>'
                   + f'<text x="{x}" y="{cy + 114}" text-anchor="middle" {SANS} font-size="17" fill="{MUTED}">{sub}</text>')
    for x in (490, 910):
        out.append(f'<polygon points="{x - 9},{cy - 8} {x + 7},{cy} {x - 9},{cy + 8}" fill="{GOLD}"/>')
    body = f'''  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="24" fill="url(#bg)" stroke="{LINE}" stroke-width="2"/>
  <text x="44" y="46" {SEMI} font-size="14" letter-spacing="4" fill="{GOLD}">HOW I WORK</text>
  {"".join(out)}'''
    return svg(W, H, body)


def divider():
    W, H = 1400, 30
    body = f'''  <rect width="{W}" height="{H}" fill="{BG0}" opacity="0"/>
  <line x1="120" y1="15" x2="640" y2="15" stroke="{GOLD}" stroke-width="1.2" opacity="0.7"/>
  <line x1="760" y1="15" x2="1280" y2="15" stroke="{GOLD}" stroke-width="1.2" opacity="0.7"/>
  {star8(700, 15, 12, fill="none", stroke=GOLD, stroke_width="1.4")}
  {star8(700, 15, 5, fill=GOLD)}
  <polygon points="660,15 666,10 672,15 666,20" fill="{TEAL}"/>
  <polygon points="728,15 734,10 740,15 734,20" fill="{TEAL}"/>'''
    return svg(W, H, body)


# ---- build + export --------------------------------------------------------------
def inkscape():
    found = shutil.which("inkscape")
    return found or r"C:\Program Files\Inkscape\bin\inkscape.exe"


def export(name):
    subprocess.run([inkscape(), str(SRC / f"{name}.src.svg"), "--export-type=svg", "--export-plain-svg",
                    "--export-text-to-path", f"--export-filename={ASSETS / f'{name}.svg'}"],
                   check=True, capture_output=True)
    # Inkscape copies the phrase groups' hidden-by-default CSS onto the converted
    # text paths, which would hide them forever; the CSS animation handles it.
    out = ASSETS / f"{name}.svg"
    out.write_text(out.read_text(encoding="utf-8").replace(";opacity:0;", ";"), encoding="utf-8")


def text_widths(name, ids):
    widths = {}
    for i in ids:
        r = subprocess.run([inkscape(), str(SRC / f"{name}.src.svg"), f"--query-id={i}", "--query-width"],
                           capture_output=True, text=True)
        try:
            widths[i] = float(r.stdout.strip())
        except ValueError:
            pass
    return widths


def main():
    files = {
        "header": header(),
        "now-building": now_building(),
        "journey": journey(),
        "how-i-work": how_i_work(),
        "divider": divider(),
    }
    for kind, *rest in CARDS:
        files[f"card-{kind}"] = card(kind, *rest)
    # typing needs measured text widths: draft, measure, rebuild
    (SRC / "typing.src.svg").write_text(typing({}), encoding="utf-8")
    files["typing"] = typing(text_widths("typing", [f"p{i}" for i in range(len(PHRASES))]))
    for name, content in files.items():
        (SRC / f"{name}.src.svg").write_text(content, encoding="utf-8")
        export(name)
        print("exported", name)


if __name__ == "__main__":
    main()
