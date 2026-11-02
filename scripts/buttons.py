#!/usr/bin/env python3
"""Rounded link buttons for the profile README, drawn as SVG.

Shields.io badges are square, and its icon set no longer includes LinkedIn,
so these are drawn here. Run `python scripts/buttons.py` after editing.
"""

from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "buttons"
COPPER, WHITE = "#8a4f28", "#ffffff"
H, PAD, ICON = 38, 16, 16
SCHOLAR_PATH = "M5.242 13.769L0 9.5 12 0l12 9.5-5.242 4.269C17.548 11.249 14.978 9.5 12 9.5c-2.977 0-5.548 1.748-6.758 4.269zM12 10a7 7 0 1 0 0 14 7 7 0 0 0 0-14z"
FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"


def linkedin_icon(x: float, y: float) -> str:
    return (f'<rect x="{x}" y="{y}" width="{ICON}" height="{ICON}" rx="3" fill="{WHITE}"/>'
            f'<text x="{x + ICON / 2}" y="{y + 12.3}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" '
            f'font-weight="700" font-size="11" fill="{COPPER}">in</text>')


def grid_icon(x: float, y: float) -> str:
    """Four rounded squares: a simple 'projects' glyph."""
    g, gap = (ICON - 3) / 2, 3
    return "".join(f'<rect x="{x + cx * (g + gap):.1f}" y="{y + cy * (g + gap):.1f}" width="{g:.1f}" height="{g:.1f}" rx="1.8" '
                   f'fill="none" stroke="{WHITE}" stroke-width="1.5"/>' for cx in (0, 1) for cy in (0, 1))


def globe_icon(x: float, y: float) -> str:
    c, r = (x + ICON / 2, y + ICON / 2), ICON / 2 - 0.8
    s = f'stroke="{WHITE}" stroke-width="1.4" fill="none"'
    return (f'<circle cx="{c[0]}" cy="{c[1]}" r="{r}" {s}/>'
            f'<ellipse cx="{c[0]}" cy="{c[1]}" rx="{r * 0.45:.2f}" ry="{r}" {s}/>'
            f'<line x1="{x + 0.8}" y1="{c[1]}" x2="{x + ICON - 0.8}" y2="{c[1]}" {s}/>')


def scholar_icon(x: float, y: float) -> str:
    # Google Scholar glyph from Simple Icons (CC0), stored here so builds need no network.
    d = SCHOLAR_PATH
    return f'<path transform="translate({x},{y}) scale({ICON / 24})" d="{d}" fill="{WHITE}"/>'


BUTTONS = [("projects", "Projects", grid_icon), ("linkedin", "LinkedIn", linkedin_icon), ("website", "jonandonibaranda.com", globe_icon),
           ("scholar", "Google Scholar", scholar_icon)]


def render(label: str, icon) -> str:
    text_w = len(label) * 7.7
    w = round(PAD + ICON + 9 + text_w + PAD)
    iy = (H - ICON) / 2
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{H}" viewBox="0 0 {w} {H}" role="img" aria-label="{label}">
<rect width="{w}" height="{H}" rx="{H / 2}" fill="{COPPER}"/>
{icon(PAD, iy)}
<text x="{PAD + ICON + 9}" y="{H / 2 + 4.6}" font-family="{FONT}" font-size="13.5" font-weight="600" fill="{WHITE}">{label}</text>
</svg>
"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for slug, label, icon in BUTTONS:
        (OUT / f"{slug}.svg").write_text(render(label, icon), encoding="utf-8")
    print(f"wrote {len(BUTTONS)} buttons to {OUT}")


if __name__ == "__main__":
    main()
