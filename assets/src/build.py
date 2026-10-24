"""Build the profile README graphics.

Run from the repository root:

    python assets/src/build.py

Writes one light and one dark SVG for every graphic into assets/. The README picks the
variant that matches the viewer's GitHub theme with a <picture> element.

Everything GitHub needs from an SVG it shows through <img> is respected here: no scripts,
no external fonts or images (screenshots are embedded as data URIs from assets/shots/),
and only CSS animations that live inside the file. Standard library only.
"""
from __future__ import annotations

import base64
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets"
SHOTS = ASSETS / "shots"

FONT = "'Helvetica Neue', Helvetica, Arial, sans-serif"
ACCENT = "#ff3b2f"
PALETTES = {
    "light": dict(bg="#ffffff", ink="#0f0f0f", dim="#6a6a6a", rule="#e4e4e4", acc=ACCENT, panel="#f4f4f4"),
    "dark": dict(bg="#0f0f0f", ink="#f5f5f5", dim="#9a9a9a", rule="#2a2a2a", acc=ACCENT, panel="#1a1a1a"),
}

# Facts shown on the featured block. Update these when the Dubai project is rebuilt.
DUBAI = dict(sales="109,706", communities="147", model_err="7.8%", baseline_err="10.9%", coverage="78%")


def shot(name: str) -> str:
    data = (SHOTS / name).read_bytes()
    return "data:image/jpeg;base64," + base64.b64encode(data).decode()


def svg(w: int, h: int, body: str, title: str, style: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">'
        f"<title>{title}</title><style>text{{font-family:{FONT}}}{style}</style>{body}</svg>"
    )


def grid(p: dict, h: int, cols: tuple[int, ...]) -> str:
    return "".join(f'<line x1="{x}" x2="{x}" y1="0" y2="{h}" stroke="{p["rule"]}"/>' for x in cols)


def label(p: dict, x: int, y: int, text: str) -> str:
    return f'<text x="{x}" y="{y}" font-size="14" font-weight="700" letter-spacing="1" fill="{p["acc"]}">{text}</text>'


def slide_x(cls: str, delay: float = 0.1) -> str:
    return (f".{cls}{{transform:scaleX(0);transform-origin:0 0;animation:{cls}-in .9s cubic-bezier(.7,0,.2,1) {delay}s forwards}}"
            f"@keyframes {cls}-in{{to{{transform:scaleX(1)}}}}")


def slide_y(cls: str, delay: float = 0.1) -> str:
    return (f".{cls}{{transform:scaleY(0);transform-origin:0 0;animation:{cls}-in .8s cubic-bezier(.7,0,.2,1) {delay}s forwards}}"
            f"@keyframes {cls}-in{{to{{transform:scaleY(1)}}}}")


# 01 + 02 ------------------------------------------------------------------ header
def header(p: dict) -> str:
    body = f"""
    <rect width="1200" height="440" fill="{p['bg']}"/>{grid(p, 440, (600, 900))}
    <rect class="bar" x="0" y="0" width="1200" height="16" fill="{p['acc']}"/>
    <text x="40" y="190" font-size="120" font-weight="700" fill="{p['ink']}" letter-spacing="-6">Hamdan</text>
    <text x="40" y="306" font-size="120" font-weight="700" fill="{p['ink']}" letter-spacing="-6">Esmail</text>
    {label(p, 620, 90, "01  WHO")}
    <text x="620" y="124" font-size="19" fill="{p['ink']}">Data Science &amp; AI undergraduate,</text>
    <text x="620" y="150" font-size="19" fill="{p['ink']}">United Arab Emirates University.</text>
    {label(p, 920, 90, "02  WHAT")}
    <text x="920" y="124" font-size="19" fill="{p['ink']}">I ship small, finished tools</text>
    <text x="920" y="150" font-size="19" fill="{p['ink']}">and games that people use.</text>
    <line x1="620" x2="1160" y1="230" y2="230" stroke="{p['rule']}"/>
    <text x="620" y="262" font-size="13" fill="{p['dim']}">BASED IN THE UAE</text>
    <text x="920" y="262" font-size="13" fill="{p['dim']}">OPEN TO INTERNSHIPS &amp; RESEARCH</text>
    <text x="620" y="330" font-size="13" fill="{p['dim']}">PYTHON  &#183;  TYPESCRIPT  &#183;  DATA  &#183;  GAMES</text>
    <text x="920" y="330" font-size="13" fill="{p['dim']}">GITHUB.COM/HAMDANESMAIL</text>
    <text x="40" y="400" font-size="13" fill="{p['dim']}">PROFILE  &#183;  2026</text>
    <text x="1160" y="400" text-anchor="end" font-size="13" fill="{p['dim']}">SHEET 1 / 1</text>"""
    return svg(1200, 440, body, "Hamdan Esmail. 01 Who: Data Science and AI undergraduate, United Arab Emirates University. 02 What: I ship small, finished tools and games that people use.", slide_x("bar"))


# small tags for the markdown lines ---------------------------------------------
def tag(p: dict, text: str, w: int) -> str:
    body = (f'<rect width="4" height="22" fill="{p["acc"]}"/>'
            f'<text x="12" y="16" font-size="13" font-weight="700" letter-spacing="1" fill="{p["acc"]}">{text}</text>')
    return svg(w, 22, body, text)


# 04 ----------------------------------------------------------------------- featured
def odometer(p: dict, x: int, y: int, steps: list[str], final: str, delay: float, size: int = 52) -> str:
    lh = size + 8
    n = len(steps)
    idn = f"o{x}"
    lines = "".join(
        f'<text x="0" y="{size + i * lh}" font-size="{size}" font-weight="700" letter-spacing="-2" fill="{p["ink"]}">{s}</text>'
        for i, s in enumerate(steps + [final]))
    return (f'<g transform="translate({x},{y})"><clipPath id="{idn}"><rect x="-4" y="0" width="300" height="{size + 12}"/></clipPath>'
            f'<g clip-path="url(#{idn})"><g style="animation:{idn} 1.3s steps({n},end) {delay}s forwards">{lines}</g></g></g>'
            f"<style>@keyframes {idn}{{to{{transform:translateY(-{n * lh}px)}}}}</style>")


def featured(p: dict) -> str:
    d = DUBAI
    body = f"""
    <rect width="1200" height="420" fill="{p['bg']}"/>{grid(p, 420, (300, 600, 900))}
    <rect class="fb" x="0" y="0" width="16" height="420" fill="{p['acc']}"/>
    {label(p, 48, 52, "04  FEATURED  &#183;  DATA")}
    <image href="{shot('dubai-property-prices.jpg')}" x="48" y="76" width="520" height="300" preserveAspectRatio="xMidYMin slice"/>
    <text x="620" y="110" font-size="44" font-weight="700" letter-spacing="-2" fill="{p['ink']}">Dubai property prices</text>
    <text x="620" y="146" font-size="16" fill="{p['ink']}">What flats and villas sell for per square metre in each</text>
    <text x="620" y="170" font-size="16" fill="{p['ink']}">Dubai community, from every 2026 sale registered with the</text>
    <text x="620" y="194" font-size="16" fill="{p['ink']}">Dubai Land Department. A model scored only on months it</text>
    <text x="620" y="218" font-size="16" fill="{p['ink']}">never saw, and a static explorer anyone can use.</text>
    <line x1="620" x2="1160" y1="246" y2="246" stroke="{p['rule']}"/>
    {odometer(p, 620, 262, ["0", "41,200", "88,900"], d['sales'], .5)}
    <text x="620" y="352" font-size="12" fill="{p['dim']}">CLEANED SALES, {d['communities']} COMMUNITIES</text>
    {odometer(p, 840, 262, ["0.0%", "4.1%", "6.9%"], d['model_err'], .8)}
    <text x="840" y="352" font-size="12" fill="{p['dim']}">MODEL ERROR, VS {d['baseline_err']} BASELINE</text>
    {odometer(p, 1010, 262, ["0%", "35%", "61%"], d['coverage'], 1.1)}
    <text x="1010" y="352" font-size="12" fill="{p['dim']}">INSIDE THE 80% INTERVAL</text>
    <text x="620" y="398" font-size="13" font-weight="700" letter-spacing="1" fill="{p['acc']}">EXPLORER  &#8594;  REPOSITORY  &#8594;  HOW THE DATA WAS CLEANED</text>"""
    return svg(1200, 420, body,
               f"04 Featured: Dubai property prices. {d['sales']} cleaned sales across {d['communities']} communities. "
               f"{d['model_err']} model error against a {d['baseline_err']} baseline. {d['coverage']} of later sales inside the 80% interval.",
               slide_y("fb"))


# 05 ----------------------------------------------------------------------- project posters
def poster(p: dict, num: str, title: str, line1: str, line2: str, fact: str, art: str, extra_style: str = "") -> str:
    body = f"""
    <rect width="580" height="430" fill="{p['bg']}"/><line x1="290" x2="290" y1="0" y2="430" stroke="{p['rule']}"/>
    <rect class="pb" x="0" y="0" width="580" height="10" fill="{p['acc']}"/>
    {label(p, 24, 44, num)}
    {art}
    <text x="24" y="318" font-size="30" font-weight="700" letter-spacing="-1" fill="{p['ink']}">{title}</text>
    <text x="24" y="346" font-size="14" fill="{p['ink']}">{line1}</text>
    <text x="24" y="366" font-size="14" fill="{p['ink']}">{line2}</text>
    <line x1="24" x2="556" y1="384" y2="384" stroke="{p['rule']}"/>
    <text x="24" y="408" font-size="12" fill="{p['dim']}">{fact}</text>"""
    return svg(580, 430, body, f"{num} {title}. {line1} {line2}", slide_x("pb", 0.2) + extra_style)


def shot_art(name: str) -> str:
    return f'<image href="{shot(name)}" x="24" y="64" width="532" height="220" preserveAspectRatio="xMidYMin slice"/>'


def study_sprint_art(p: dict) -> tuple[str, str]:
    c = 2 * math.pi * 80
    art = f"""<rect x="24" y="64" width="532" height="220" fill="{p['panel']}"/>
    <g transform="translate(140,174)"><circle r="80" fill="none" stroke="{p['rule']}" stroke-width="14"/>
      <circle class="ring" r="80" fill="none" stroke="{p['acc']}" stroke-width="14" stroke-dasharray="{c:.1f}" stroke-dashoffset="{c * .25:.1f}" transform="rotate(-90)"/>
      <text y="12" text-anchor="middle" font-size="36" font-weight="700" letter-spacing="-1" fill="{p['ink']}">25:00</text></g>
    <text x="260" y="140" font-size="12" font-weight="700" letter-spacing="1" fill="{p['acc']}">ONE TASK</text>
    <text x="260" y="176" font-size="24" font-weight="700" letter-spacing="-1" fill="{p['ink']}">Problem set 4</text>
    <text x="260" y="204" font-size="14" fill="{p['dim']}">Statistics  &#183;  focus 25, break 5</text>"""
    style = ".ring{animation:ring 2.4s cubic-bezier(.4,0,.2,1) .4s forwards}@keyframes ring{to{stroke-dashoffset:0}}"
    return art, style


def projects(p: dict) -> dict[str, str]:
    ss_art, ss_style = study_sprint_art(p)
    return {
        "project-keepers-lantern": poster(p, "05.1  GAME", "Keeper's Lantern",
                                          "A survival game about a lantern and a forest that",
                                          "moves every night. Made for Hack Club Terra.",
                                          "PHASER 3  &#183;  202 TESTS  &#183;  SOUND MADE IN CODE  &#183;  PLAYS IN THE BROWSER",
                                          shot_art("keepers-lantern.jpg")),
        "project-firstrole": poster(p, "05.2  TOOL", "FirstRole",
                                    "A job finder for students that reads public careers",
                                    "pages and shows every source it used.",
                                    "TYPESCRIPT  &#183;  CLOUDFLARE WORKERS  &#183;  NEVER APPLIES FOR YOU  &#183;  LIVE",
                                    shot_art("firstrole.jpg")),
        "project-coursesignal": poster(p, "05.3  TOOL", "CourseSignal",
                                       "A student copilot in iMessage: text a question,",
                                       "get a short answer backed by a page you can tap.",
                                       "TYPESCRIPT  &#183;  TINYFISH AGENTS  &#183;  TOUCHES YOUR CALENDAR ONLY ON APPROVAL",
                                       shot_art("coursesignal.jpg")),
        "project-study-sprint": poster(p, "05.4  TOOL", "Study Sprint",
                                       "A local-first focus timer. Pick one task, run a sprint,",
                                       "keep your queue after a refresh. No account, no server.",
                                       "PLAIN JAVASCRIPT  &#183;  JSON BACKUPS  &#183;  KEYBOARD SHORTCUTS  &#183;  LIVE",
                                       ss_art, ss_style),
    }


# 06 ----------------------------------------------------------------------- toolkit
def toolkit(p: dict) -> str:
    cols = [
        ("DATA", ["Python", "pandas", "LightGBM", "scikit-learn", "matplotlib", "pytest"]),
        ("WEB", ["TypeScript", "JavaScript", "Phaser 3", "Vite", "Cloudflare Workers", "HTML &amp; CSS"]),
        ("PRACTICE", ["Tests and CI on every repo", "GitHub Pages and Cloudflare", "Git", "Plain-English READMEs",
                      "Temporal validation", "Documented cleaning rules"]),
    ]
    items = ""
    for c, (head, lst) in enumerate(cols):
        x = 48 + c * 372
        items += f'<text x="{x}" y="96" font-size="12" font-weight="700" letter-spacing="1" fill="{p["dim"]}">{head}</text>'
        for i, t in enumerate(lst):
            y = 120 + i * 30
            items += (f'<g class="tk" style="animation-delay:{.2 + c * .15 + i * .06:.2f}s">'
                      f'<line x1="{x}" x2="{x + 330}" y1="{y + 8}" y2="{y + 8}" stroke="{p["rule"]}"/>'
                      f'<text x="{x}" y="{y}" font-size="15" fill="{p["ink"]}">{t}</text></g>')
    body = f"""<rect width="1200" height="320" fill="{p['bg']}"/>{grid(p, 320, (420, 792))}
    <rect x="0" y="0" width="1200" height="10" fill="{p['acc']}"/>
    {label(p, 48, 52, "06  TOOLKIT")}{items}"""
    style = ".tk{opacity:0;animation:tk .5s ease forwards}@keyframes tk{to{opacity:1}}"
    return svg(1200, 320, body, "06 Toolkit. Data: Python, pandas, LightGBM, scikit-learn, matplotlib, pytest. Web: TypeScript, JavaScript, Phaser 3, Vite, Cloudflare Workers, HTML and CSS. Practice: tests and CI on every repo, GitHub Pages and Cloudflare, Git, plain-English READMEs, temporal validation, documented cleaning rules.", style)


# 08 ----------------------------------------------------------------------- contact
def hello(p: dict) -> str:
    body = (f'<rect class="hb" width="300" height="56" fill="{p["acc"]}"/>'
            f'<text x="24" y="36" font-size="17" font-weight="700" letter-spacing="1" fill="#ffffff">SAY HELLO  &#8594;</text>')
    return svg(300, 56, body, "Say hello", slide_x("hb", 0.2))


def build() -> list[Path]:
    written = []
    for theme, p in PALETTES.items():
        files = {
            "header": header(p),
            "tag-now": tag(p, "03  NOW", 96),
            "featured": featured(p),
            **projects(p),
            "toolkit": toolkit(p),
            "tag-education": tag(p, "07  EDUCATION", 150),
            "tag-contact": tag(p, "08  CONTACT", 130),
            "hello": hello(p),
        }
        for name, content in files.items():
            path = ASSETS / f"{name}-{theme}.svg"
            path.write_text(content, encoding="utf-8")
            written.append(path)
    return written


if __name__ == "__main__":
    for path in build():
        print(f"{path.relative_to(ROOT)}  {path.stat().st_size / 1024:.0f} KB")
