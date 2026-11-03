#!/usr/bin/env python3
"""Terminal window for the profile README: the contribution snake and the tools
I use, framed as a short typed session. SVG + SMIL so it animates inside
GitHub's <img>.

    python scripts/terminal.py --snake dist/snake-light.svg --out dist/terminal.svg

The snake is generated daily by Platane/snk in the workflow and nested here as
an inner <svg>; its CSS (custom properties on :root, classes .c/.s/.u and
keyframes c*/s*/u*) is left untouched, so everything of ours uses a "tm-" prefix.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ICONS = json.loads((HERE / "icons.json").read_text())

BG, BORDER, BAR, PROMPT, CMD, OUT, TITLE, ICON = (
    "#f4f1ec", "#d8d2c8", "#ebe6de", "#8a4f28", "#111111", "#4a453f", "#6b655e", "#8a4f28")
MONO = "Menlo, 'SF Mono', Consolas, 'DejaVu Sans Mono', monospace"
SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
PROMPT_TEXT = "jon@chicago ~ $ "
CW = 8.1                       # monospace character width at 13.5px
W, PAD = 940, 30
EASE = 'calcMode="spline" keyTimes="0;1" keySplines=".22 1 .36 1"'   # ease-out


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def fade(begin: float, dur: float = .3) -> str:
    """Fade in from transparent instead of popping."""
    return f'<animate attributeName="opacity" values="0;1" {EASE} begin="{begin:.2f}s" dur="{dur}s" fill="freeze"/>'


def rise(begin: float, dy: float, dur: float) -> str:
    """Drift up into place while fading in."""
    return (f'<animateTransform attributeName="transform" type="translate" values="0 {dy};0 0" {EASE} '
            f'begin="{begin:.2f}s" dur="{dur}s" fill="freeze"/>')


def typed(x: float, y: float, text: str, begin: float, cid: str) -> tuple[str, float]:
    """A prompt that appears, then a command that types out. Returns (svg, end time)."""
    cx = x + len(PROMPT_TEXT) * CW
    steps = ";".join(f"{i * CW:.1f}" for i in range(len(text) + 1))
    dur = len(text) * 0.05
    svg = (f'<text class="tm-m" x="{x}" y="{y}" fill="{PROMPT}" opacity="0">{esc(PROMPT_TEXT)}{fade(begin)}</text>'
           f'<clipPath id="tm-{cid}"><rect x="{cx:.1f}" y="{y - 15}" height="20" width="0">'
           f'<animate attributeName="width" values="{steps}" calcMode="discrete" begin="{begin + .2:.2f}s" dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>'
           f'<text class="tm-m" x="{cx:.1f}" y="{y}" fill="{CMD}" clip-path="url(#tm-{cid})">{esc(text)}</text>')
    return svg, begin + 0.2 + dur


def snake_block(path: Path | None, x: float, y: float, width: float, begin: float) -> tuple[str, float]:
    if not path or not path.exists():
        return (f'<text class="tm-m" x="{x}" y="{y + 40}" fill="{OUT}">(the snake is drawn by the daily workflow)</text>', 40.0)
    src = path.read_text(encoding="utf-8")
    m = re.match(r'\s*<svg([^>]*)>(.*)</svg>\s*$', src, re.S)
    attrs, inner = m.group(1), m.group(2)
    vb = re.search(r'viewBox="([^"]+)"', attrs).group(1)
    vw, vh = (float(v) for v in vb.split()[2:4])
    height = width * vh / vw
    return (f'<g opacity="0">{fade(begin, .9)}{rise(begin, 10, 1)}'
            f'<svg x="{x}" y="{y}" width="{width:.1f}" height="{height:.1f}" viewBox="{vb}">{inner}</svg></g>', height)


def tools_block(x: float, y: float, width: float, begin: float) -> tuple[str, float]:
    cols = 7
    cell = width / cols
    parts = []
    for i, tool in enumerate(ICONS):
        r, c = divmod(i, cols)
        cx, cy = x + c * cell + cell / 2, y + r * 74
        t = begin + i * 0.07
        size = 30
        parts.append(f'<g opacity="0">{fade(t, .5)}{rise(t, 8, .6)}'
                     f'<path transform="translate({cx - size / 2:.1f},{cy:.1f}) scale({size / 24})" d="{tool["d"]}" fill="{ICON}"/>'
                     f'<text class="tm-n" x="{cx:.1f}" y="{cy + size + 17:.1f}" text-anchor="middle" fill="{OUT}">{esc(tool["name"])}</text></g>')
    rows = (len(ICONS) + cols - 1) // cols
    return "".join(parts), rows * 74, begin + len(ICONS) * 0.07


def render(snake: Path | None) -> str:
    x = PAD
    parts = []
    y = 64
    s, t = typed(x, y, "contributions --last-year", 0.5, "a")
    parts.append(s)
    snake_svg, snake_h = snake_block(snake, x - 8, y + 10, W - 2 * PAD + 16, t + 0.25)
    parts.append(snake_svg)
    y = y + 10 + snake_h + 14
    parts.append(f'<text class="tm-m" x="{x}" y="{y}" fill="{OUT}" opacity="0">Each square is a day of GitHub contributions.'
                 f'{fade(t + 0.6, .6)}</text>')
    y += 40
    s, t2 = typed(x, y, "tools", t + 1.2, "b")
    parts.append(s)
    tools_svg, tools_h, t3 = tools_block(x, y + 18, W - 2 * PAD, t2 + 0.3)
    parts.append(tools_svg)
    y = y + 18 + tools_h + 18
    parts.append(f'<text class="tm-m" x="{x}" y="{y}" fill="{PROMPT}" opacity="0">{esc(PROMPT_TEXT)}{fade(t3 + 0.2)}</text>'
                 f'<rect x="{x + len(PROMPT_TEXT) * CW:.1f}" y="{y - 13}" width="{CW:.1f}" height="16" fill="{PROMPT}" opacity="0">'
                 f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1.1s" begin="{t3 + 0.2:.2f}s" repeatCount="indefinite"/></rect>')
    H = round(y + 26)
    frame = (f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="8" fill="{BG}" stroke="{BORDER}"/>'
             f'<rect x=".5" y=".5" width="{W - 1}" height="30" rx="8" fill="{BAR}"/>'
             f'<rect x=".5" y="22" width="{W - 1}" height="9" fill="{BAR}"/>'
             f'<line x1="0" y1="31" x2="{W}" y2="31" stroke="{BORDER}"/>'
             f'<text x="{W / 2:.0f}" y="20" text-anchor="middle" fill="{TITLE}" style="font:12px {SANS}">jon@chicago: ~</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="Terminal showing this year\'s GitHub contributions as a snake animation, and the tools I use: '
            f'{", ".join(t["name"] for t in ICONS)}.">'
            f'<style>.tm-m{{font:13.5px {MONO};white-space:pre}}.tm-n{{font:11px {MONO}}}</style>'
            f'{frame}{"".join(parts)}</svg>\n')


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--snake", type=Path)
    ap.add_argument("--out", type=Path, default=HERE.parent / "assets" / "terminal.svg")
    a = ap.parse_args()
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(render(a.snake), encoding="utf-8")
    print(f"wrote {a.out}")
