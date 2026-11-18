"""The header that plays the portfolio site by itself, and the small gold buttons.

The header is nine "skins", one per world. Each rises through the one before it as a curtain,
the way the site changes colour, while the figure names the world and jumps to the next.
"""
from __future__ import annotations

from pieces import (GOLD, GOLD_INK, HOLD, N, STEP, TOTAL, WIPE, WORLDS, header_frames, ink_width, inked, mask, place,
                    shot, squares, svg)


def header() -> str:
    W, H = 1200, 640
    name_size = 172
    hb = place("hamdan", name_size, 34, 156)
    eb = place("esmail", name_size, 1166, 608, "r")
    nb = place("l-nine-worlds", 40, 36, 604)
    win = (556, 174, 464, 290)
    bx, by = 216, 176
    defs = [mask("mh", "hamdan", hb), mask("me", "esmail", eb), mask("mn", "l-nine-worlds", nb),
            f'<clipPath id="win"><rect x="{win[0]}" y="{win[1]}" width="{win[2]}" height="{win[3]}" rx="4"/></clipPath>']
    skins = []
    for i, (name, bg, ink, _live, _line) in enumerate(WORLDS):
        lid = f"l-{name.lower()}"
        label = place(lid, 38, bx + 20, by + 48)
        a = ink_width(lid, 38)
        inner = max(a + 16 + 31, 137)
        bw, bh = inner + 40, 92
        defs.append(mask(f"ml{i}", lid, label))
        dots = "".join(f'<circle class="d d{n}" cx="{bx + 20 + a + 19 + n * 12:.1f}" cy="{by + 40}" r="3.5" fill="{bg}"/>' for n in range(3))
        bubble = (f'<rect x="{bx}" y="{by}" width="{bw:.1f}" height="{bh}" fill="{ink}"/>'
                  f'<rect x="{bx + 8}" y="{by + bh}" width="16" height="10" fill="{ink}"/>'
                  f'<rect x="{bx}" y="{by + bh + 10}" width="8" height="8" fill="{ink}"/>'
                  f'{inked(f"ml{i}", label, bg)}<g class="dots">{dots}</g>{squares(bx + 20, by + 65, i, bg)}')
        body = (f'<rect width="{W}" height="{H}" fill="{bg}"/>{inked("mh", hb, ink)}{inked("me", eb, ink)}{inked("mn", nb, ink)}'
                f'<image href="{shot(name, 520, 66)}" x="{win[0]}" y="{win[1]}" width="{win[2]}" height="{win[3]}" '
                f'preserveAspectRatio="xMidYMin slice" clip-path="url(#win)"/>{bubble}')
        if i == 0:
            # The first world is never hidden: it is what shows when nothing moves.
            skins.append(f"<g>{body}</g>")
            continue
        start, end = (i * STEP - WIPE) / TOTAL, i * STEP / TOTAL
        ease = ".65 0 .35 1"
        if i < N - 1:
            clip = (f'values="{H};{H};0;0" keyTimes="0;{start:.5f};{end:.5f};1" keySplines="0 0 1 1;{ease};0 0 1 1"')
            vis = f'values="hidden;visible;hidden" keyTimes="0;{start:.5f};{(i + 1) * STEP / TOTAL:.5f}"'
        else:  # the last world also leaves, upward, to show the first one again
            clip = (f'values="{H};{H};0;0;-{H}" keyTimes="0;{start:.5f};{end:.5f};{(TOTAL - WIPE) / TOTAL:.5f};1" '
                    f'keySplines="0 0 1 1;{ease};0 0 1 1;{ease}"')
            vis = f'values="hidden;visible" keyTimes="0;{start:.5f}"'
        defs.append(f'<clipPath id="c{i}"><rect x="0" y="{H}" width="{W}" height="{H}">'
                    f'<animate attributeName="y" calcMode="spline" dur="{TOTAL}s" repeatCount="indefinite" {clip}/></rect></clipPath>')
        skins.append(f'<g clip-path="url(#c{i})" visibility="hidden">'
                     f'<animate attributeName="visibility" calcMode="discrete" dur="{TOTAL}s" repeatCount="indefinite" {vis}/>{body}</g>')

    frames, (fx, fy, fw, fh) = header_frames()
    gx, gy = 22, 236

    def frame(cls: str, f: str) -> str:
        return f'<image class="f {cls}" href="{frames[f]}" x="{gx + fx}" y="{gy + fy}" width="{fw}" height="{fh}"/>'

    guide = (f'<ellipse class="ground" cx="{gx + 110}" cy="{gy + 231}" rx="50" ry="7" fill="#000" opacity=".22"/>'
             f'<g class="hop"><g class="loop">{frame("idle", "idle")}{frame("ta", "talk3")}{frame("tb", "talk6")}{frame("air", "air")}</g>'
             f'<g class="hi">{frame("w1", "wave1")}{frame("w2", "wave2")}</g></g>')

    hold = HOLD / STEP * 100           # where in each world's turn the curtain starts
    talk = 40.0                         # he talks for the first part of each turn
    slots = 10
    ta = "".join(f"{talk / slots * n:.2f}%{{opacity:{1 if n % 2 == 0 else 0}}}" for n in range(slots)) + f"{talk}%{{opacity:0}}"
    tb = "".join(f"{talk / slots * n:.2f}%{{opacity:{0 if n % 2 == 0 else 1}}}" for n in range(slots)) + f"{talk}%{{opacity:0}}"
    hi = talk / 100 * STEP              # the first hello lasts as long as one line
    style = f"""
.f{{opacity:0}}
.idle{{animation:idle {STEP}s steps(1) infinite}}@keyframes idle{{0%{{opacity:0}}{talk}%{{opacity:1}}{hold:.2f}%{{opacity:0}}}}
.air{{animation:air {STEP}s steps(1) infinite}}@keyframes air{{0%{{opacity:0}}{hold:.2f}%{{opacity:1}}}}
.ta{{animation:ta {STEP}s steps(1) infinite}}@keyframes ta{{{ta}}}
.tb{{animation:tb {STEP}s steps(1) infinite}}@keyframes tb{{{tb}}}
.loop{{animation:gone {hi}s steps(1) 1}}@keyframes gone{{0%{{opacity:0}}100%{{opacity:0}}}}
.hi{{opacity:0;animation:here {hi}s steps(1) 1}}@keyframes here{{0%{{opacity:1}}100%{{opacity:1}}}}
.w1{{animation:w1 .3s steps(1) infinite}}@keyframes w1{{0%{{opacity:1}}50%{{opacity:0}}}}
.w2{{animation:w2 .3s steps(1) infinite}}@keyframes w2{{0%{{opacity:0}}50%{{opacity:1}}}}
.hop{{animation:hop {STEP}s infinite}}
@keyframes hop{{0%,{hold:.2f}%{{transform:translateY(0);animation-timing-function:cubic-bezier(.2,.7,.4,1)}}{(hold + 100) / 2:.2f}%{{transform:translateY(-36px);animation-timing-function:cubic-bezier(.6,0,.8,.4)}}100%{{transform:translateY(0)}}}}
.ground{{transform-box:fill-box;transform-origin:center;animation:ground {STEP}s infinite}}
@keyframes ground{{0%,{hold:.2f}%{{transform:scale(1)}}{(hold + 100) / 2:.2f}%{{transform:scale(.72)}}100%{{transform:scale(1)}}}}
.dots{{animation:dots {STEP}s steps(1) infinite}}@keyframes dots{{0%{{opacity:1}}{talk}%{{opacity:0}}}}
.d{{animation:bob .62s ease-in-out infinite}}.d1{{animation-delay:.12s}}.d2{{animation-delay:.24s}}
@keyframes bob{{0%,60%,100%{{transform:translateY(0)}}30%{{transform:translateY(-5px)}}}}
@media (prefers-reduced-motion:reduce){{.rest{{display:none}}.f,.hop,.ground,.dots,.d,.loop,.hi{{animation:none}}.idle{{opacity:1}}.dots{{opacity:0}}}}
"""
    body = f'<defs>{"".join(defs)}</defs>{skins[0]}<g class="rest">{"".join(skins[1:])}</g>{guide}'
    names = ", ".join(w[0] for w in WORLDS)
    return svg(W, H, body, f"Hamdan Esmail. Nine worlds: {names}. A small 3D figure of Hamdan names each one as the page changes colour.", style)


def button(wid: str, label: str) -> str:
    size = 21
    w = round(ink_width(wid, size) + 52)
    box = place(wid, size, 26, 35)
    return svg(w, 56, f'<defs>{mask("m", wid, box)}</defs><rect width="{w}" height="56" fill="{GOLD}"/>{inked("m", box, GOLD_INK)}', label)
