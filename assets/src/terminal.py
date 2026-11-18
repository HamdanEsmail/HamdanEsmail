"""The terminal that draws him, then tells you who he is. One stand-alone animated SVG.

The frames of the figure come from capture/guide-terminal.html. With motion turned off, or
where animation is not supported, the finished state is what shows.
"""
from __future__ import annotations

import pieces as m

GOLD = "#c9a45a"
FACTS = [("studies", "data science and AI at UAEU"), ("based", "United Arab Emirates"), ("speaks", "Arabic and English"),
         ("writes", "TypeScript, Python, Dart"), ("likes", "software that is finished")]


def terminal() -> str:
    W, H, LOOP = 1200, 620, 32.0
    BG, BAR, BONE, MUTE = "#0c0a08", "#181512", "#f1f0ed", "#a39d96"
    CW, LH, X0, Y0 = 15, 40, 40, 112          # one character, one line, where the text starts
    frames, (fx, fy, fw, fh), boxes = m.terminal_frames()
    css: list[str] = []
    ids = iter(range(10 ** 6))

    def pct(t: float) -> str:
        return f"{t / LOOP * 100:.4f}%"

    def shown(wins: list, rest: int) -> str:
        """A class that is visible only inside these time windows. `rest` is what it is with motion off."""
        n = f"v{next(ids)}"
        stops = "".join(f"{pct(a)}{{opacity:1}}" + ("" if b >= LOOP else f"{pct(b)}{{opacity:0}}") for a, b in wins)
        first = "" if wins[0][0] == 0 else "0%{opacity:0}"
        last = "100%{opacity:1}" if wins[-1][1] >= LOOP else "100%{opacity:0}"
        css.append(f".{n}{{opacity:{rest};animation:{n} {LOOP}s steps(1) infinite}}@keyframes {n}{{{first}{stops}{last}}}")
        return n

    def after(t: float) -> str:
        return shown([(t, LOOP)], 1)

    def text(col: float, row: int, s: str, fill: str, cls: str = "") -> str:
        s = s.replace("&", "&amp;").replace("<", "&lt;")
        c = f' class="{cls}"' if cls else ""
        return f'<text{c} x="{X0 + col * CW}" y="{Y0 + row * LH}" textLength="{len(s) * CW}" fill="{fill}">{s}</text>'

    def typed(row: int, cmd: str, start: float, end: float, until: float, prompt_at: float) -> str:
        """A prompt, a command typed one letter at a time, and the cursor that leads it."""
        n, w = f"t{next(ids)}", len(cmd) * CW
        css.append(f".{n}{{transform:translateX({w}px);animation:{n} {LOOP}s infinite}}"
                   f"@keyframes {n}{{0%{{transform:translateX(0)}}{pct(start)}{{transform:translateX(0);animation-timing-function:steps({len(cmd)})}}"
                   f"{pct(end)}{{transform:translateX({w}px)}}100%{{transform:translateX({w}px)}}}}")
        x, y = X0 + 2 * CW, Y0 + row * LH
        line = (f'{text(0, row, "$", GOLD)}{text(2, row, cmd, BONE)}'
                f'<rect class="{n}" x="{x - 1}" y="{y - 27}" width="{w + 4}" height="38" fill="{BG}"/>'
                f'<g class="{shown([(prompt_at, until)], 0)}"><rect class="{n}" x="{x + 1}" y="{y - 22}" width="13" height="28" fill="{GOLD}"/></g>')
        return line if prompt_at == 0 else f'<g class="{after(prompt_at)}">{line}</g>'

    # When things happen, in seconds.
    T_DRAW, T_PARTS, T_READY, T_SPIN = 2.0, (2.7, 3.3, 3.9, 4.5), 5.0, 5.1
    T_ABOUT, T_FACTS, T_WORLDS, T_LAST, T_SPIN2 = 7.2, 8.9, 11.2, 13.4, 21.0
    spin_end = T_SPIN + 1.5
    wave = (T_FACTS, T_FACTS + 1.8)

    rows = [typed(0, "node guide.js", 0.5, 1.7, T_DRAW, 0),
            text(2, 1, f"drawing one figure from {boxes} boxes", MUTE, after(T_DRAW))]
    for (label, col), t in zip((("kandura", 2), ("arms", 13), ("head", 21), ("ghutra", 29)), T_PARTS):
        rows.append(f'<g class="{after(t)}">{text(col, 2, "+", GOLD)}{text(col + 2, 2, label, BONE)}</g>')
    rows.append(text(2, 3, "ready. checking all sides", MUTE, after(T_READY)))
    rows.append(typed(4, "hamdan --about", T_ABOUT + 0.2, T_ABOUT + 1.4, T_FACTS, T_ABOUT))
    for i, (key, val) in enumerate(FACTS):
        rows.append(f'<g class="{after(T_FACTS + i * 0.35)}">{text(2, 5 + i, key, MUTE)}{text(12, 5 + i, val, BONE)}</g>')
    rows.append(typed(10, "hamdan --worlds", T_WORLDS + 0.2, T_WORLDS + 1.5, T_WORLDS + 1.8, T_WORLDS))
    rows.append(text(2, 11, "nine, all live. keep scrolling.", BONE, after(T_WORLDS + 1.8)))
    rows.append(f'<g class="{after(T_LAST)}">{text(0, 12, "$", GOLD)}'
                f'<rect class="blink" x="{X0 + 2 * CW + 1}" y="{Y0 + 12 * LH - 22}" width="13" height="28" fill="{GOLD}"/></g>')
    css.append(".blink{animation:blink 1.1s steps(1) infinite}@keyframes blink{0%{opacity:1}55%{opacity:0}}")

    # The preview on the right: the same figure the site draws, one frame at a time.
    px, py, k = 800, 164, 1.2
    seen = {"outline": [(T_DRAW, T_PARTS[0])], "body": [(T_PARTS[0], T_PARTS[1])], "arms": [(T_PARTS[1], T_PARTS[2])],
            "head": [(T_PARTS[2], T_PARTS[3])], "wave1": [], "wave2": []}
    for n in range(1, 16):
        seen[f"spin{n:02d}"] = [(s0 + (n - 1) * 0.1, s0 + n * 0.1) for s0 in (T_SPIN, T_SPIN2)]
    slot = 0.15
    for n in range(round((wave[1] - wave[0]) / slot)):
        seen["wave1" if n % 2 == 0 else "wave2"].append((wave[0] + n * slot, wave[0] + (n + 1) * slot))
    seen["idle"] = [(T_PARTS[3], T_SPIN), (spin_end, wave[0]), (wave[1], T_SPIN2), (T_SPIN2 + 1.5, LOOP)]
    figure = "".join(
        f'<image class="{shown(wins, 1 if f == "idle" else 0)}" href="{frames[f]}" x="{px + fx * k:.1f}" y="{py + fy * k:.1f}" '
        f'width="{fw * k:.1f}" height="{fh * k:.1f}"/>' for f, wins in seen.items())
    count = f"{boxes} boxes"
    pane = (f'<rect x="800" y="84" width="360" height="506" fill="{BAR}"/>'
            f'<ellipse class="{after(T_PARTS[0])}" cx="{px + 150 * k:.0f}" cy="{py + 317 * k:.0f}" rx="62" ry="8" fill="#000000" opacity=".35"/>{figure}'
            f'<text class="{after(T_DRAW)}" x="820" y="118" style="font-size:17px" textLength="{len(count) * 10.2:.0f}" fill="{MUTE}">{count}</text>')
    path = "portfolio / js / guide.js"
    bar = (f'<rect width="{W}" height="56" fill="{BAR}"/>'
           + "".join(f'<rect x="{26 + n * 20}" y="23" width="10" height="10" fill="{MUTE}" opacity="{0.9 - n * 0.25:.2f}"/>' for n in range(3))
           + f'<text x="104" y="35" style="font-size:18px" textLength="{len(path) * 10.8:.0f}" fill="{MUTE}">{path}</text>')
    style = ("text{font-family:ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono','DejaVu Sans Mono',monospace;font-size:25px}"
             + "".join(css) + "@media (prefers-reduced-motion:reduce){*{animation:none!important}}")
    body = f'<rect width="{W}" height="{H}" fill="{BG}"/>{bar}{"".join(rows)}{pane}'
    said = "; ".join(f"{a} {b}" for a, b in FACTS)
    return m.svg(W, H, body, f"A terminal. The command node guide.js draws a small 3D figure of Hamdan from {boxes} boxes: kandura, arms, head, ghutra. "
                           f"Then hamdan --about prints: {said}. Then hamdan --worlds prints: nine, all live.", style)
