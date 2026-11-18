"""About, How I got here, and one band per world.

Each function returns one stand-alone SVG. Everything is complete and readable when nothing
moves: the animation only adds to a finished picture.
"""
from __future__ import annotations

import pieces as m
from pieces import FEET, FRAME_H, MID

GOLD, BONE, DARK, WARM = "#c9a45a", "#f1f0ed", "#0c0a08", "#191410"


class Clock:
    """Collects the CSS for one loop: what is visible when, and what moves where."""

    def __init__(self, loop: float, prefix: str):
        self.loop, self.prefix, self.css, self.n = loop, prefix, [], 0

    def pct(self, t: float) -> str:
        return f"{max(0.0, min(self.loop, t)) / self.loop * 100:.4f}%"

    def name(self) -> str:
        self.n += 1
        return f"{self.prefix}{self.n}"

    def shown(self, wins: list, rest: int) -> str:
        """A class visible only inside these time windows. `rest` is what it is when nothing moves."""
        wins = sorted((a, b) for a, b in wins if b > a)
        n = self.name()
        if not wins:
            self.css.append(f".{n}{{opacity:{rest}}}")
            return n
        stops = "".join(f"{self.pct(a)}{{opacity:1}}" + ("" if b >= self.loop else f"{self.pct(b)}{{opacity:0}}") for a, b in wins)
        first = "" if wins[0][0] <= 0 else "0%{opacity:0}"
        last = "100%{opacity:1}" if wins[-1][1] >= self.loop else "100%{opacity:0}"
        self.css.append(f".{n}{{opacity:{rest};animation:{n} {self.loop}s steps(1) infinite}}@keyframes {n}{{{first}{stops}{last}}}")
        return n

    def rest_of(self, wins: list) -> list:
        out, t = [], 0.0
        for a, b in sorted(wins):
            if a > t:
                out.append((t, a))
            t = max(t, b)
        if t < self.loop:
            out.append((t, self.loop))
        return out

    def move(self, keys: list, prop: str = "transform") -> str:
        """A class whose `prop` passes through these (time, value, easing) keys."""
        n = self.name()
        body = "".join(f"{self.pct(t)}{{{prop}:{v}" + (f";animation-timing-function:{e}" if e else "") + "}" for t, v, e in keys)
        self.css.append(f".{n}{{animation:{n} {self.loop}s linear infinite}}@keyframes {n}{{{body}}}")
        return n

    def style(self) -> str:
        return "".join(self.css)


STILL = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"


def flap(a: float, b: float, slot: float) -> tuple[list, list]:
    """Two frames taking turns between a and b."""
    one, two, n, t = [], [], 0, a
    while t < b - 1e-6:
        (one if n % 2 == 0 else two).append((t, min(b, t + slot)))
        t += slot
        n += 1
    return one, two


def figure(clock: Clock, frames: dict, box: tuple, x0: float, y0: float, seen: dict, idle: str = "idle") -> str:
    """The stack of frames at one place. Whatever no other frame claims belongs to `idle`."""
    fx, fy, fw, fh = box
    taken = [w for f, wins in seen.items() if f != idle for w in wins]
    seen = dict(seen)
    seen[idle] = clock.rest_of(taken)
    return "".join(
        f'<image class="{clock.shown(wins, 1 if f == idle else 0)}" href="{frames[f]}" x="{x0 + fx:.1f}" y="{y0 + fy:.1f}" '
        f'width="{fw:.1f}" height="{fh:.1f}"/>' for f, wins in seen.items())


# ---------------------------------------------------------------- About: what I do, and the one rule, said by him
def about() -> str:
    W, LOOP = 1200, 18.0
    size = min(124, 670 / max(m.ink_width("h-build", 1), m.ink_width("h-open", 1)))
    y1 = 56 + 0.72 * size
    y2 = y1 + 0.95 * size
    s_first = y2 + 92
    s_last = s_first + (m.word("b-statement")["lines"] - 1) * 55
    f_first = s_last + 84
    f_last = f_first + (m.word("b-finished")["lines"] - 1) * 50
    H = max(780, round(f_last + 70))
    boxes = {"h1": m.place("h-build", size, 44, y1), "h2": m.place("h-open", size, 44, y2),
             "st": m.place("b-statement", 44, 44, s_first), "fi": m.place("b-finished", 40, 44, f_first)}
    q_lines = m.word("b-quote")["lines"]
    bw, bh = 416, 60 + (q_lines - 1) * 50 + 66
    bx, by = 1160 - bw, 56
    boxes["q"] = m.place("b-quote", 40, bx + 30, by + 62)
    defs = [m.mask(f"m-{k}", wid, boxes[k]) for k, wid in
            (("h1", "h-build"), ("h2", "h-open"), ("st", "b-statement"), ("fi", "b-finished"), ("q", "b-quote"))]

    clock = Clock(LOOP, "s")
    talk = (0.0, 2.6)
    dots_cls = clock.shown([talk], 0)

    def skin(field: str, ink: str, bubble: str, bubble_ink: str) -> str:
        dots = "".join(f'<circle class="d d{n}" cx="{bx + 36 + n * 17}" cy="{by + bh - 30}" r="5" fill="{bubble_ink}"/>' for n in range(3))
        return (f'<rect width="{W}" height="{H}" fill="{field}"/>'
                + "".join(m.inked(f"m-{k}", boxes[k], ink) for k in ("h1", "h2", "st", "fi"))
                + f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="{bubble}"/>'
                  f'<rect x="{bx + 198}" y="{by + bh}" width="22" height="14" fill="{bubble}"/>'
                  f'<rect x="{bx + 214}" y="{by + bh + 14}" width="12" height="12" fill="{bubble}"/>'
                + m.inked("m-q", boxes["q"], bubble_ink) + f'<g class="{dots_cls}">{dots}</g>')

    # The curtain: gold rests, the dark field rises through the words, stays, and leaves the same way.
    up, down = (8.0, 8.9), (LOOP - 0.9, LOOP)
    ease = ".65 0 .35 1"
    defs.append(f'<clipPath id="cut"><rect x="0" y="{H}" width="{W}" height="{H}">'
                f'<animate attributeName="y" calcMode="spline" dur="{LOOP}s" repeatCount="indefinite" values="{H};{H};0;0;-{H}" '
                f'keyTimes="0;{up[0] / LOOP:.5f};{up[1] / LOOP:.5f};{down[0] / LOOP:.5f};1" keySplines="0 0 1 1;{ease};0 0 1 1;{ease}"/></rect></clipPath>')
    second = (f'<g class="rest" clip-path="url(#cut)" visibility="hidden">'
              f'<animate attributeName="visibility" calcMode="discrete" dur="{LOOP}s" repeatCount="indefinite" values="hidden;visible" keyTimes="0;{up[0] / LOOP:.5f}"/>'
              f'{skin(WARM, BONE, GOLD, DARK)}</g>')

    unit_h = 436
    k = unit_h / FRAME_H
    x0, y0 = 985 - MID * k, (H - 44) - FEET * k
    frames, box = m.poses(["idle", "talkA", "talkB", "glasses", "aroundA", "aroundB", "wave1", "wave2"], unit_h)
    ta, tb = flap(*talk, 0.16)
    w1, w2 = flap(15.0, 16.65, 0.15)
    seen = {"talkA": ta, "talkB": tb, "glasses": [(5.6, 7.2)], "aroundA": [(10.6, 11.8)], "aroundB": [(11.8, 13.0)], "wave1": w1, "wave2": w2}
    guide = (f'<ellipse cx="985" cy="{H - 42}" rx="118" ry="13" fill="#000000" opacity=".2"/>'
             + figure(clock, frames, box, x0, y0, seen))
    style = (clock.style() + ".d{animation:bob .62s ease-in-out infinite}.d1{animation-delay:.12s}.d2{animation-delay:.24s}"
             "@keyframes bob{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-6px)}}"
             "@media (prefers-reduced-motion:reduce){.rest{display:none}}" + STILL)
    body = f'<defs>{"".join(defs)}</defs>{skin(GOLD, DARK, DARK, GOLD)}{second}{guide}'
    said = " ".join(m.word(w)["text"] for w in ("b-statement", "b-finished"))
    return m.svg(W, H, body, f"I build things you can open. {said} A 3D figure of Hamdan says: {m.word('b-quote')['text']}", style)


# ---------------------------------------------------------------- About: how I got here, a path he hops down
YEARS = ["2020", "2025", "2025", "2026"]


def journey() -> str:
    W, STEP, HOP = 1200, 4.2, 0.9
    LOOP = STEP * len(YEARS)
    tops, y = [], 172
    for i in range(len(YEARS)):
        tops.append(y)
        y += max(150, m.word(f"j-{i}")["lines"] * 50) + 46
    H = y + 14
    dim = 0.42
    clock, beat = Clock(LOOP, "j"), Clock(STEP, "b")
    head = m.place("h-journey", 62, 44, 104)
    defs, rows = [m.mask("m-h", "h-journey", head)], []
    for i, year in enumerate(YEARS):
        yb = m.place(f"y-{year}", 96, 178, tops[i] + 67)
        sb = m.place(f"j-{i}", 40, 440, tops[i] + 33)
        defs += [m.mask(f"m-y{i}", f"y-{year}", yb), m.mask(f"m-s{i}", f"j-{i}", sb)]
        a, b = i * STEP - 0.25, i * STEP + STEP - HOP + 0.15
        keys = ([(0, 1, None), (b, 1, None), (b + 0.3, dim, None), (LOOP - 0.55, dim, None), (LOOP - 0.25, 1, None), (LOOP, 1, None)] if i == 0
                else [(0, dim, None), (a - 0.3, dim, None), (a, 1, None), (b, 1, None), (b + 0.3, dim, None), (LOOP, dim, None)])
        rows.append(f'<g class="{clock.move(keys, "opacity")}">{m.inked(f"m-y{i}", yb, GOLD)}{m.inked(f"m-s{i}", sb, BONE)}</g>')

    # He rests beside one year, then jumps to the next with a full turn, as he does between worlds on the site.
    unit_h = 163
    k = unit_h / FRAME_H
    spins = [f"spin{n:02d}" for n in range(1, 16)]
    frames, box = m.poses(["idle"] + spins, unit_h, 48)
    rest = STEP - HOP
    seen = {s: [(rest + n * HOP / 15, rest + (n + 1) * HOP / 15)] for n, s in enumerate(spins)}
    x0, y0 = 92 - MID * k, tops[0] + 142 - FEET * k
    jump, ground = [], []
    for i in range(len(YEARS)):
        nxt = (i + 1) % len(YEARS)
        d, dn, t0 = tops[i] - tops[0], tops[nxt] - tops[0], i * STEP
        jump += [(t0, f"translateY({d}px)", None), (t0 + rest, f"translateY({d}px)", "cubic-bezier(.2,.7,.4,1)")]
        jump.append((t0 + rest + 0.3, f"translateY({d - 30}px)", "cubic-bezier(.6,0,.8,.4)") if nxt > i
                    else (t0 + rest + 0.6, f"translateY({dn - 30}px)", "cubic-bezier(.3,0,.7,1)"))
        ground += [(t0, f"translateY({d}px)", None), (t0 + rest, f"translateY({d}px)", "cubic-bezier(.5,0,.5,1)")]
    jump.append((LOOP, "translateY(0px)", None))
    ground.append((LOOP, "translateY(0px)", None))
    guide = (f'<ellipse class="{clock.move(ground)}" cx="92" cy="{tops[0] + 143}" rx="44" ry="6" fill="#000000" opacity=".5"/>'
             f'<g class="{clock.move(jump)}">{figure(beat, frames, box, x0, y0, seen)}</g>')
    body = (f'<defs>{"".join(defs)}</defs><rect width="{W}" height="{H}" fill="{DARK}"/>{m.inked("m-h", head, BONE)}'
            f'{"".join(rows)}{guide}')
    told = " ".join(f"{yr}: {m.word(f'j-{i}')['text']}" for i, yr in enumerate(YEARS))
    return m.svg(W, H, body, f"How I got here. {told}", clock.style() + beat.style() + STILL)


# ---------------------------------------------------------------- one band per world, and something of his own in each
def band(i: int) -> str:
    name, bg, ink, _live, line = m.WORLDS[i]
    key = name.lower()
    W, LOOP = 1200, 12.0
    lines = m.word(f"s-{key}")["lines"]
    H = max(470, 262 + lines * 50 + 30)
    size = min(140, 650 / max(m.ink_width(f"w-{w[0].lower()}", 1) for w in m.WORLDS))
    nb = m.place(f"w-{key}", size, 44, 196)
    sb = m.place(f"s-{key}", 40, 44, 262)
    px, py, pw, ph = 728, 44, 432, 270
    tag = (1002, H - 90, 158, 46)
    tb = m.place("t-open-it", 22, tag[0] + 42, tag[1] + 31)
    defs = (f'{m.mask("mn", f"w-{key}", nb)}{m.mask("ms", f"s-{key}", sb)}{m.mask("mt", "t-open-it", tb)}'
            f'<clipPath id="c"><rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="4"/></clipPath>')

    unit_h = 272
    k = unit_h / FRAME_H
    cx = 744
    x0, y0 = cx - MID * k, (H - 34) - FEET * k
    clock = Clock(LOOP, "w")
    s = 0.6 + i * 1.0                       # each world takes its turn, so the tower is never all moving at once
    wrap, seen = "", {}
    if key == "falaj":                      # he waves hello
        seen["wave1"], seen["wave2"] = flap(s, s + 1.8, 0.15)
    elif key == "backed":                   # he points at the proof
        seen["point"] = [(s, s + 2.4)]
    elif key == "standing":                 # "right now": he checks his watch
        seen["watch"] = [(s, s + 2.4)]
    elif key == "fineprint":                # the small print: he pushes his glasses up
        seen["glasses"] = [(s, s + 2.0)]
    elif key == "redtape":                  # he jumps the tape, twice
        seen["air"] = [(s, s + 0.7), (s + 1.0, s + 1.7)]
        up, down = "cubic-bezier(.2,.7,.4,1)", "cubic-bezier(.6,0,.8,.4)"
        keys = [(0, "translateY(0px)", None)]
        for a in (s, s + 1.0):
            keys += [(a, "translateY(0px)", up), (a + 0.35, "translateY(-44px)", down), (a + 0.7, "translateY(0px)", None)]
        wrap = clock.move(keys + [(LOOP, "translateY(0px)", None)])
    elif key == "groundwork":               # he looks over the records, one side then the other
        seen["aroundA"], seen["aroundB"] = [(s, s + 1.1)], [(s + 1.1, s + 2.2)]
    elif key == "upstream":                 # he walks off, and comes back upstream
        leg, stride = 2.4, 0.6
        for side, a in (("walkR", s), ("walkL", s + leg)):
            for f in range(8):
                seen[f"{side}{f}"] = [(a + c * stride + f * stride / 8, a + c * stride + (f + 1) * stride / 8) for c in range(round(leg / stride))]
        wrap = clock.move([(0, "translateX(0px)", None), (s, "translateX(0px)", None), (s + leg, "translateX(150px)", None),
                           (s + 2 * leg, "translateX(0px)", None), (LOOP, "translateX(0px)", None)])
    elif key == "knock":                    # he knocks on the picture
        seen["point"] = [(s + a, s + a + 0.16) for a in (0, 0.32, 0.64, 1.5, 1.82, 2.14)]
    else:                                   # the last world: he turns once to take it all in
        seen = {f"spin{n:02d}": [(s + (n - 1) * 0.08, s + n * 0.08)] for n in range(1, 16)}
    frames, box = m.poses(["idle"] + list(seen), unit_h)
    ground = f'<ellipse cx="{cx}" cy="{H - 33}" rx="72" ry="9" fill="#000000" opacity=".2"/>'
    guide = figure(clock, frames, box, x0, y0, seen)
    if key == "upstream":
        guide = f'<g class="{wrap}">{ground}{guide}</g>'
    elif wrap:
        guide = f'{ground}<g class="{wrap}">{guide}</g>'
    else:
        guide = ground + guide
    body = (f'<defs>{defs}</defs><rect width="{W}" height="{H}" fill="{bg}"/>{m.squares(46, 40, i, ink, 10, 8)}'
            f'{m.inked("mn", nb, ink)}{m.inked("ms", sb, ink)}'
            f'<image href="{m.shot(name, 720, 76)}" x="{px}" y="{py}" width="{pw}" height="{ph}" preserveAspectRatio="xMidYMin slice" clip-path="url(#c)"/>'
            f'<rect x="{tag[0]}" y="{tag[1]}" width="{tag[2]}" height="{tag[3]}" fill="{ink}"/>'
            f'<rect x="{tag[0] + 18}" y="{tag[1] + 18}" width="10" height="10" fill="{bg}"/>{m.inked("mt", tb, bg)}'
            f'{guide}')
    return m.svg(W, H, body, f"{name}, world {i + 1} of {len(m.WORLDS)}. {line}", clock.style() + STILL)
