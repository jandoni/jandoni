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


GITHUB_PATH = "M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"


def github_icon(x: float, y: float) -> str:
    """GitHub mark from Simple Icons (CC0)."""
    return f'<path transform="translate({x},{y}) scale({ICON / 24})" d="{GITHUB_PATH}" fill="{WHITE}"/>'


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


BUTTONS = [("linkedin", "LinkedIn", linkedin_icon), ("scholar", "Google Scholar", scholar_icon),
           ("github-projects", "Projects", github_icon), ("website", "jonandonibaranda.com", globe_icon)]


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
