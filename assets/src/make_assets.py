"""Generate every image in the profile README (cinematic red-noir theme).

Run:  python assets/src/make_assets.py
It writes *.src.svg files here, then exports them with Inkscape (text
converted to paths, so fonts look the same everywhere) into assets/.
"""
import random
import shutil
import subprocess
from pathlib import Path

# ---- palette -----------------------------------------------------------
BLACK, BG0, BG1, BG2 = "#050506", "#09070A", "#120A0C", "#1C0E10"
LINE = "#3A1E20"
RED, RED_HOT, EMBER = "#C8102E", "#FF4D4D", "#FF7A45"
TEXT, MUTED, DIM = "#EDE6E3", "#A8999A", "#6E5E60"
CYAN = "#70CFCF"          # Echo's eye ring: the one cool accent
FONT = 'font-family="Bahnschrift"'

SRC = Path(__file__).parent
ASSETS = SRC.parent


def defs_common():
    return f'''
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{BG0}"/><stop offset="1" stop-color="{BG1}"/>
    </linearGradient>
    <radialGradient id="vignette" cx="0.5" cy="0.5" r="0.75">
      <stop offset="0.55" stop-color="{BLACK}" stop-opacity="0"/>
      <stop offset="1" stop-color="{BLACK}" stop-opacity="0.85"/>
    </radialGradient>
    <linearGradient id="redline" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{RED}" stop-opacity="0"/>
      <stop offset="0.15" stop-color="{RED_HOT}"/>
      <stop offset="1" stop-color="{RED}" stop-opacity="0"/>
    </linearGradient>
    <filter id="grain" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="11"/>
      <feColorMatrix type="saturate" values="0"/>
    </filter>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="6"/>
    </filter>'''


STYLE = '''
  <style>
    @keyframes breathe { 0%, 100% { opacity: 0.75; } 50% { opacity: 1; } }
    @keyframes drift { 0% { transform: translateY(0); opacity: 0; } 15% { opacity: 0.8; } 100% { transform: translateY(-140px); opacity: 0; } }
    @keyframes pulse { 0%, 100% { opacity: 0.35; transform: scale(1); } 50% { opacity: 1; transform: scale(1.4); } }
    @keyframes eye { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }
    .breathe { animation: breathe 7s ease-in-out infinite; }
    .dust { animation: drift 9s linear infinite; }
    .pulse { transform-box: fill-box; transform-origin: center; animation: pulse 2.4s ease-in-out infinite; }
    .eye { animation: eye 4s ease-in-out infinite; }
    @media (prefers-reduced-motion: reduce) {
      .breathe, .dust, .pulse, .eye { animation: none !important; }
      .dust { opacity: 0; }
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


def finish(w, h, letterbox=True):
    bars = (f'<rect width="{w}" height="18" fill="{BLACK}"/>'
            f'<rect y="{h - 18}" width="{w}" height="18" fill="{BLACK}"/>') if letterbox else ""
    return (f'  <rect width="{w}" height="{h}" fill="url(#vignette)"/>\n'
            f'  <rect width="{w}" height="{h}" filter="url(#grain)" opacity="0.06"/>\n  {bars}')


def dust(rng, x0, x1, y0, y1, n):
    out = []
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        out.append(f'<circle class="dust" style="animation-delay:-{rng.uniform(0, 9):.1f}s;animation-duration:{rng.uniform(7, 12):.1f}s" '
                   f'cx="{x:.0f}" cy="{y:.0f}" r="{rng.choice([0.8, 1, 1.3, 1.6])}" fill="{EMBER}"/>')
    return "\n    ".join(out)


def caged_lamp(cx, cy):
    return f'''<g>
    <circle cx="{cx}" cy="{cy + 10}" r="90" fill="{RED}" opacity="0.22" filter="url(#glow)"/>
    <rect x="{cx - 34}" y="{cy - 6}" width="68" height="34" rx="10" fill="{RED_HOT}" class="breathe"/>
    <rect x="{cx - 34}" y="{cy - 6}" width="68" height="34" rx="10" fill="none" stroke="{BLACK}" stroke-width="3"/>
    <g stroke="{BLACK}" stroke-width="3">
      <line x1="{cx - 17}" y1="{cy - 6}" x2="{cx - 17}" y2="{cy + 28}"/>
      <line x1="{cx}" y1="{cy - 6}" x2="{cx}" y2="{cy + 28}"/>
      <line x1="{cx + 17}" y1="{cy - 6}" x2="{cx + 17}" y2="{cy + 28}"/>
      <line x1="{cx - 34}" y1="{cy + 11}" x2="{cx + 34}" y2="{cy + 11}"/>
    </g>
    <rect x="{cx - 40}" y="{cy - 14}" width="80" height="9" rx="2" fill="#1A1012"/>
  </g>'''


# ---- 1. header ------------------------------------------------------------
def header():
    W, H = 1400, 420
    rng = random.Random(4)
    ribs = "".join(f'<rect x="{x}" y="0" width="14" height="{H}" fill="#140A0C" opacity="0.9"/>'
                   for x in range(620, 1400, 120))
    body = f'''  <rect width="{W}" height="{H}" fill="{BG0}"/>
  <radialGradient id="haze" cx="0.78" cy="0.15" r="0.75">
    <stop offset="0" stop-color="{RED}" stop-opacity="0.55"/>
    <stop offset="0.45" stop-color="{RED}" stop-opacity="0.12"/>
    <stop offset="1" stop-color="{RED}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="beam" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{RED_HOT}" stop-opacity="0.30"/>
    <stop offset="1" stop-color="{RED}" stop-opacity="0"/>
  </linearGradient>
  {ribs}
  <rect x="560" y="300" width="840" height="3" fill="#1E0F11"/>
  <rect width="{W}" height="{H}" fill="url(#haze)"/>
  <polygon class="breathe" points="1010,60 1160,60 1330,{H} 700,{H}" fill="url(#beam)"/>
  {caged_lamp(1085, 46)}
  {caged_lamp(1290, 46)}
  <g>
    {dust(rng, 760, 1320, 120, 400, 36)}
  </g>
  <text x="92" y="132" {FONT} font-weight="600" font-size="15" letter-spacing="6" fill="{RED_HOT}">CALLSIGN  —  VECTOR</text>
  <text x="88" y="216" {FONT} font-weight="700" font-size="86" letter-spacing="5" fill="{TEXT}">HAMDAN ESMAIL</text>
  <text x="92" y="262" {FONT} font-size="18" letter-spacing="5" fill="{MUTED}">DATA SCIENCE &amp; ARTIFICIAL INTELLIGENCE  ·  UAEU</text>
  <rect x="92" y="290" width="520" height="2" fill="url(#redline)"/>
  <text x="92" y="330" {FONT} font-size="14" letter-spacing="4" fill="{DIM}">NOW BUILDING  BORROWED ALIBI</text>
{finish(W, H)}'''
    return svg(W, H, body)


# ---- 2. typing line --------------------------------------------------------
PHRASES = [
    "Data Science & AI student at UAEU",
    "Building tools students actually use",
    "Making Borrowed Alibi, a browser mystery game",
]


def typing(widths):
    W, H = 1400, 76
    n = len(PHRASES)
    period = 4 * n
    style = "\n  <style>\n"
    groups = []
    for i, phrase in enumerate(PHRASES):
        w = widths.get(f"p{i}", 600)
        vis_end = 100 / n
        style += (f"    @keyframes vis{i} {{ 0% {{ opacity: 1; }} {vis_end - 0.5:.2f}% {{ opacity: 1; }} "
                  f"{vis_end:.2f}% {{ opacity: 0; }} 100% {{ opacity: 0; }} }}\n"
                  f"    @keyframes type{i} {{ 0% {{ transform: translateX(0); }} {vis_end * 0.55:.2f}% "
                  f"{{ transform: translateX({w + 6:.0f}px); }} 100% {{ transform: translateX({w + 6:.0f}px); }} }}\n"
                  f"    .g{i} {{ opacity: 0; animation: vis{i} {period}s linear {i * 4}s infinite; }}\n"
                  f"    .c{i} {{ animation: type{i} {period}s steps({len(phrase)}) {i * 4}s infinite; }}\n")
        groups.append(f'''  <g class="g{i}">
    <text id="p{i}" x="84" y="48" {FONT} font-size="26" letter-spacing="0.5" fill="{TEXT}">{phrase.replace("&", "&amp;")}</text>
    <g class="c{i}">
      <rect x="82" y="14" width="1280" height="50" fill="{BG1}"/>
      <rect class="blink" x="84" y="22" width="3" height="32" fill="{RED_HOT}"/>
    </g>
  </g>''')
    style += ("    @keyframes blink { 0%, 49% { opacity: 1; } 50%, 100% { opacity: 0; } }\n"
              "    .blink { animation: blink 1s steps(1) infinite; }\n"
              "    @media (prefers-reduced-motion: reduce) { .g0 { opacity: 1 !important; animation: none !important; }"
              " .g1, .g2 { animation: none !important; } .c0 { animation: none !important; transform: translateX(2000px); }"
              " .blink { animation: none !important; } }\n  </style>")
    body = f'''  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="10" fill="{BG1}" stroke="{LINE}" stroke-width="2"/>
  <rect x="1" y="1" width="5" height="{H - 2}" fill="{RED}"/>
  <polygon points="44,30 52,38 44,46 36,38" fill="{RED_HOT}"/>
{chr(10).join(groups)}'''
    return svg(W, H, body, style)


# ---- 3. flagship banner (Borrowed Alibi) -------------------------------------
ECHO = '''
    <ellipse cx="878" cy="442" rx="30" ry="6" fill="#000" opacity="0.7"/>
    <path d="M 866,402 L 868,438 L 876,438 L 876,402 Z" fill="#2A1D20" stroke="#000" stroke-width="1.5"/>
    <path d="M 880,402 L 880,438 L 889,438 L 889,402 Z" fill="#3A2629" stroke="#000" stroke-width="1.5"/>
    <path d="M 865,436 L 877,436 L 877,442 L 861,442 Z" fill="#160E10" stroke="#000" stroke-width="1.2"/>
    <path d="M 879,436 L 891,436 L 891,442 L 875,442 Z" fill="#160E10" stroke="#000" stroke-width="1.2"/>
    <path d="M 858,292 Q 878,284 898,292 L 902,350 L 906,410 Q 880,416 852,410 L 856,350 Z" fill="#120A0C" stroke="#000" stroke-width="2"/>
    <path d="M 896,296 L 900,350 L 904,408" fill="none" stroke="#FF4D4D" stroke-width="1.6" opacity="0.85"/>
    <path d="M 860,294 Q 878,287 896,294" fill="none" stroke="#FF7A45" stroke-width="1.4" opacity="0.8"/>
    <path d="M 858,296 L 852,352 L 856,370 L 863,368 L 864,352 Z" fill="#0E0809" stroke="#000" stroke-width="1.5"/>
    <rect x="852" y="364" width="11" height="3" fill="#70CFCF"/>
    <path d="M 853,367 L 856,384 L 862,384 L 863,367 Z" fill="#3A2629" stroke="#000" stroke-width="1.2"/>
    <path d="M 898,296 L 902,352 L 900,370 L 893,368 L 892,352 Z" fill="#160D0F" stroke="#000" stroke-width="1.5"/>
    <path d="M 900,300 L 902,352" stroke="#FF4D4D" stroke-width="1" opacity="0.8"/>
    <path d="M 893,367 L 893,384 L 899,384 L 901,367 Z" fill="#5A3236" stroke="#000" stroke-width="1.2"/>
    <rect x="873" y="276" width="10" height="12" fill="#2A1D20" stroke="#000" stroke-width="1.2"/>
    <path d="M 866,256 Q 866,246 878,246 Q 891,246 891,258 L 890,272 Q 884,282 874,281 Q 866,278 865,268 Z" fill="#2E2023" stroke="#000" stroke-width="1.8"/>
    <path d="M 878,246 Q 891,246 891,258 L 890,272 Q 886,279 880,281" fill="none" stroke="#FF4D4D" stroke-width="1.6" opacity="0.9"/>
    <rect x="866" y="259" width="10" height="2.6" rx="1.3" fill="#05090C"/>
    <rect class="eye" x="866" y="259" width="10" height="2.6" rx="1.3" fill="none" stroke="#70CFCF" stroke-width="0.9"/>'''


def flagship():
    W, H = 1400, 470
    rng = random.Random(9)
    body = f'''  <rect width="{W}" height="{H}" fill="{BG0}"/>
  <radialGradient id="pool" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="{EMBER}" stop-opacity="0.45"/>
    <stop offset="1" stop-color="{RED}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="cone" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{RED_HOT}" stop-opacity="0.32"/>
    <stop offset="1" stop-color="{RED}" stop-opacity="0.02"/>
  </linearGradient>
  <radialGradient id="side" cx="1" cy="0.3" r="0.9">
    <stop offset="0" stop-color="{RED}" stop-opacity="0.35"/>
    <stop offset="1" stop-color="{RED}" stop-opacity="0"/>
  </radialGradient>
  <rect width="{W}" height="{H}" fill="url(#side)"/>
  <rect x="640" y="388" width="760" height="2" fill="#2A1416"/>
  <rect x="640" y="390" width="760" height="62" fill="#0D0708"/>
  <line x1="1060" y1="18" x2="1060" y2="60" stroke="#1A1012" stroke-width="3"/>
  <polygon points="1040,60 1080,60 1090,82 1030,82" fill="#1A1012" stroke="#000" stroke-width="2"/>
  <ellipse cx="1060" cy="82" rx="30" ry="5" fill="{RED_HOT}" class="breathe"/>
  <polygon class="breathe" points="1034,84 1086,84 1210,400 910,400" fill="url(#cone)"/>
  <ellipse cx="1060" cy="404" rx="190" ry="26" fill="url(#pool)"/>
  <g>
    {dust(rng, 960, 1170, 140, 390, 22)}
  </g>
  <g transform="translate(1060,402) scale(1.45) translate(-878,-442)">{ECHO}
  </g>
  <text x="84" y="104" {FONT} font-weight="600" font-size="15" letter-spacing="6" fill="{RED_HOT}">FLAGSHIP PROJECT</text>
  <text x="80" y="186" {FONT} font-weight="700" font-size="70" letter-spacing="3" fill="{TEXT}">BORROWED ALIBI</text>
  <rect x="84" y="210" width="460" height="2" fill="url(#redline)"/>
  <text x="84" y="252" {FONT} font-size="21" fill="{MUTED}">An android investigation thriller you play in the browser.</text>
  <text x="84" y="282" {FONT} font-size="21" fill="{MUTED}">Read the scene. Question the witness. Decide what goes on record.</text>
  <g {FONT} font-size="13" letter-spacing="2">
    <rect x="84" y="318" width="108" height="30" rx="2" fill="none" stroke="{LINE}" stroke-width="1.6"/>
    <text x="138" y="338" text-anchor="middle" fill="{TEXT}">PHASER 3</text>
    <rect x="202" y="318" width="128" height="30" rx="2" fill="none" stroke="{LINE}" stroke-width="1.6"/>
    <text x="266" y="338" text-anchor="middle" fill="{TEXT}">JAVASCRIPT</text>
    <rect x="340" y="318" width="104" height="30" rx="2" fill="none" stroke="{LINE}" stroke-width="1.6"/>
    <text x="392" y="338" text-anchor="middle" fill="{TEXT}">SVG ART</text>
  </g>
  <circle class="pulse" cx="91" cy="386" r="5" fill="{RED_HOT}"/>
  <text x="106" y="391" {FONT} font-size="14" letter-spacing="3" fill="{DIM}">IN DEVELOPMENT  ·  A NEW CHAPTER EVERY WEEK</text>
{finish(W, H)}'''
    return svg(W, H, body)


# ---- 4. project cards -------------------------------------------------------
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
        return f'''<rect x="{cx - 32}" y="{cy - 42}" width="64" height="84" rx="4" fill="{TEXT}"/>
      <rect x="{cx - 20}" y="{cy - 28}" width="40" height="5" rx="2" fill="{BG2}"/>
      <rect x="{cx - 20}" y="{cy - 15}" width="34" height="4" rx="2" fill="{DIM}"/>
      <rect x="{cx - 20}" y="{cy - 5}" width="38" height="4" rx="2" fill="{DIM}"/>
      <rect x="{cx - 20}" y="{cy + 5}" width="26" height="4" rx="2" fill="{DIM}"/>
      <circle cx="{cx + 26}" cy="{cy + 32}" r="17" fill="{RED}"/>
      <path d="M {cx + 18},{cy + 32} l 6,6 l 10,-11" fill="none" stroke="{TEXT}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'''
    if kind == "coursesignal":
        return f'''<path d="M {cx - 40},{cy - 28} h 64 a 10 10 0 0 1 10 10 v 34 a 10 10 0 0 1 -10 10 h -40 l -16 14 v -14 h -8 a 10 10 0 0 1 -10 -10 v -34 a 10 10 0 0 1 10 -10 z" fill="{TEXT}"/>
      <circle cx="{cx - 18}" cy="{cy + 1}" r="4.5" fill="{BG2}"/><circle cx="{cx - 2}" cy="{cy + 1}" r="4.5" fill="{BG2}"/><circle cx="{cx + 14}" cy="{cy + 1}" r="4.5" fill="{BG2}"/>
      <path d="M {cx + 32},{cy - 44} a 22 22 0 0 1 16 16" fill="none" stroke="{RED_HOT}" stroke-width="3.5" stroke-linecap="round"/>
      <path d="M {cx + 34},{cy - 58} a 36 36 0 0 1 28 28" fill="none" stroke="{RED}" stroke-width="3.5" stroke-linecap="round"/>'''
    if kind == "studysprint":
        r = 38
        import math
        a = math.radians(-90 + 360 * 0.68)
        return f'''<circle cx="{cx}" cy="{cy + 4}" r="{r}" fill="none" stroke="{LINE}" stroke-width="9"/>
      <path d="M {cx},{cy + 4 - r} A {r} {r} 0 1 1 {cx + r * math.cos(a):.1f},{cy + 4 + r * math.sin(a):.1f}" fill="none" stroke="{RED}" stroke-width="9" stroke-linecap="round"/>
      <rect x="{cx - 8}" y="{cy - 48}" width="16" height="8" rx="2" fill="{TEXT}"/>
      <line x1="{cx}" y1="{cy + 4}" x2="{cx}" y2="{cy - 17}" stroke="{TEXT}" stroke-width="4" stroke-linecap="round"/>
      <line x1="{cx}" y1="{cy + 4}" x2="{cx + 13}" y2="{cy + 12}" stroke="{TEXT}" stroke-width="4" stroke-linecap="round"/>
      <circle cx="{cx}" cy="{cy + 4}" r="4" fill="{RED_HOT}"/>'''
    return f'''<circle cx="{cx}" cy="{cy}" r="46" fill="#5A2A2A"/>
      <circle cx="{cx}" cy="{cy}" r="38" fill="#2A1416"/>
      <circle cx="{cx}" cy="{cy}" r="34" fill="#07090C"/>
      <rect x="{cx - 20}" y="{cy - 4}" width="40" height="8" rx="4" fill="#05090C" stroke="{CYAN}" stroke-width="2.4"/>
      <path d="M {cx + 24},{cy - 30} A 38 38 0 0 1 {cx + 38},{cy}" fill="none" stroke="{RED_HOT}" stroke-width="2" opacity="0.8"/>'''


CARDS = [
    ("borrowedalibi", "Borrowed Alibi", "FLAGSHIP",
     "A browser investigation thriller released one chapter a week. Walk the scene, compare a recorded memory with the room, and decide what goes on record.",
     ["Phaser 3", "JavaScript", "SVG art"]),
    ("firstrole", "FirstRole", "LIVE DEMO",
     "A student job finder that reads public careers pages and turns them into a shortlist with sources, match reasons, and freshness, not invented openings.",
     ["TypeScript", "Cloudflare Workers", "TinyFish"]),
    ("coursesignal", "CourseSignal", "LIVE DEMO",
     "An evidence-first student copilot in iMessage. It finds and reads live public sources, then replies with a short, receipt-backed answer.",
     ["TypeScript", "TinyFish", "iMessage"]),
    ("studysprint", "Study Sprint", "SHIPPED",
     "A local-first focus timer: pick one task, run a sprint, and keep your queue after a refresh.",
     ["JavaScript", "HTML / CSS"]),
]


def card(kind, title, status, desc, chips):
    W, H = 700, 300
    lines = wrap(desc, 46)
    desc_svg = "".join(f'<text x="214" y="{128 + i * 25}" {FONT} font-size="17" fill="{MUTED}">{ln}</text>'
                       for i, ln in enumerate(lines))
    chip_svg, x = [], 214
    for c in chips:
        cw = 26 + len(c) * 8.1
        chip_svg.append(f'<rect x="{x}" y="{H - 62}" width="{cw:.0f}" height="30" rx="2" fill="none" stroke="{LINE}" stroke-width="1.6"/>'
                        f'<text x="{x + cw / 2:.1f}" y="{H - 41}" text-anchor="middle" {FONT} font-size="14" fill="{TEXT}">{c}</text>')
        x += cw + 10
    sw = 26 + len(status) * 9.5
    hot = status == "FLAGSHIP"
    accent = RED_HOT if hot else MUTED
    body = f'''  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="8" fill="url(#bg)" stroke="{LINE}" stroke-width="2"/>
  <rect x="1" y="1" width="5" height="{H - 2}" fill="{RED}"/>
  <radialGradient id="tileglow" cx="0.5" cy="0.5" r="0.6">
    <stop offset="0" stop-color="{RED}" stop-opacity="0.35"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/>
  </radialGradient>
  <rect x="34" y="34" width="150" height="{H - 68}" rx="6" fill="{BG0}" stroke="{LINE}" stroke-width="1.5"/>
  <rect x="34" y="34" width="150" height="{H - 68}" rx="6" fill="url(#tileglow)"/>
  <g>
      {icon(kind, 109, H / 2)}
  </g>
  <text x="212" y="82" {FONT} font-weight="700" font-size="34" letter-spacing="1" fill="{TEXT}">{title}</text>
  <rect x="{W - 34 - sw:.0f}" y="54" width="{sw:.0f}" height="28" rx="2" fill="{RED if hot else BG2}" opacity="{0.25 if hot else 1}"/>
  <rect x="{W - 34 - sw:.0f}" y="54" width="{sw:.0f}" height="28" rx="2" fill="none" stroke="{accent}" stroke-width="1.4"/>
  <text x="{W - 34 - sw / 2:.1f}" y="73" text-anchor="middle" {FONT} font-weight="600" font-size="12.5" letter-spacing="2" fill="{accent}">{status}</text>
  {desc_svg}
  {"".join(chip_svg)}
  <rect width="{W}" height="{H}" filter="url(#grain)" opacity="0.04"/>'''
    return svg(W, H, body)


# ---- 5. journey ---------------------------------------------------------------
JOURNEY = [
    ("UAEU", "B.Sc. Data Science & AI", "done"),
    ("FirstRole", "Sep 2026", "done"),
    ("CourseSignal", "Oct 2026", "done"),
    ("Study Sprint", "Oct 2026", "done"),
    ("Borrowed Alibi", "Oct 2026 → Jan 2027", "now"),
    ("Next", "Internships & research", "next"),
]


def diamond(x, y, r, **attrs):
    a = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<polygon points="{x},{y - r} {x + r},{y} {x},{y + r} {x - r},{y}" {a}/>'


def journey():
    W, H = 1400, 290
    y = 150
    xs = [110 + i * (1180 / (len(JOURNEY) - 1)) for i in range(len(JOURNEY))]
    now_i = next(i for i, j in enumerate(JOURNEY) if j[2] == "now")
    parts = [f'<line x1="{xs[0]}" y1="{y}" x2="{xs[now_i]}" y2="{y}" stroke="{RED}" stroke-width="2.4"/>',
             f'<line x1="{xs[now_i]}" y1="{y}" x2="{xs[-1]}" y2="{y}" stroke="{DIM}" stroke-width="2" stroke-dasharray="6 8"/>']
    for i, ((title, sub, state), x) in enumerate(zip(JOURNEY, xs)):
        ty = y - 52 if i % 2 == 0 else y + 60
        if state == "done":
            parts.append(diamond(x, y, 11, fill=RED) + diamond(x, y, 4, fill=BG0))
            col = TEXT
        elif state == "now":
            parts.append(f'<circle cx="{x}" cy="{y}" r="34" fill="{RED}" opacity="0.35" filter="url(#glow)"/>'
                         f'<g class="pulse">{diamond(x, y, 20, fill=RED_HOT, opacity="0.3")}</g>' + diamond(x, y, 12, fill=RED_HOT))
            col = RED_HOT
        else:
            parts.append(diamond(x, y, 10, fill=BG0, stroke=DIM, stroke_width="1.6", stroke_dasharray="3 3"))
            col = MUTED
        parts.append(f'<text x="{x:.1f}" y="{ty}" text-anchor="middle" {FONT} font-weight="600" font-size="21" fill="{col}">{title}</text>'
                     f'<text x="{x:.1f}" y="{ty + 24}" text-anchor="middle" {FONT} font-size="14.5" fill="{MUTED}">{sub.replace("&", "&amp;")}</text>')
    body = f'''  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="8" fill="url(#bg)" stroke="{LINE}" stroke-width="2"/>
  <rect x="1" y="1" width="5" height="{H - 2}" fill="{RED}"/>
  <text x="44" y="48" {FONT} font-weight="600" font-size="14" letter-spacing="5" fill="{RED_HOT}">PATH</text>
  {"".join(parts)}
  <rect width="{W}" height="{H}" filter="url(#grain)" opacity="0.04"/>'''
    return svg(W, H, body)


def divider():
    W, H = 1400, 30
    body = f'''  <rect x="120" y="14" width="560" height="1.5" fill="url(#redline)" transform="rotate(180 400 15)"/>
  <rect x="720" y="14" width="560" height="1.5" fill="url(#redline)"/>
  {diamond(700, 15, 7, fill=RED_HOT)}
  {diamond(700, 15, 12, fill="none", stroke=RED, stroke_width="1.2")}'''
    return svg(W, H, body)


# ---- build + export --------------------------------------------------------------
def inkscape():
    return shutil.which("inkscape") or r"C:\Program Files\Inkscape\bin\inkscape.exe"


def export(name):
    subprocess.run([inkscape(), str(SRC / f"{name}.src.svg"), "--export-type=svg", "--export-plain-svg",
                    "--export-text-to-path", f"--export-filename={ASSETS / f'{name}.svg'}"],
                   check=True, capture_output=True)
    # Inkscape copies the typing groups' hidden-by-default CSS onto the converted
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
    files = {"header": header(), "flagship": flagship(), "journey": journey(), "divider": divider()}
    for kind, *rest in CARDS:
        files[f"card-{kind}"] = card(kind, *rest)
    (SRC / "typing.src.svg").write_text(typing({}), encoding="utf-8")
    files["typing"] = typing(text_widths("typing", [f"p{i}" for i in range(len(PHRASES))]))
    for name, content in files.items():
        (SRC / f"{name}.src.svg").write_text(content, encoding="utf-8")
        export(name)
        print("exported", name)


if __name__ == "__main__":
    main()
