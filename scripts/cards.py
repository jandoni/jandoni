#!/usr/bin/env python3
"""Publication cards for the profile README, in the style of the project cards
on jonandonibaranda.com: dark rounded card, inset photo, title, short text,
a small label and a cream "read" pill. GitHub strips CSS, so each card is an SVG
with its photo and the portfolio's Geist fonts embedded.

    python scripts/cards.py
"""

from __future__ import annotations

import base64
import html
import io
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "cards"
PORTFOLIO = Path.home() / "Projects" / "portfolio" / "assets"
FONT_SANS = PORTFOLIO / "fonts" / "geist-latin-wght-normal.woff2"
FONT_MONO = PORTFOLIO / "fonts" / "geist-mono-latin-wght-normal.woff2"

CARD, EDGE, TITLE, BODY, LABEL, PILL, PILL_TEXT, PANEL = (
    "#1c1b1f", "#2e2d33", "#f3efe8", "#c6c0b6", "#c8895a", "#efe8dc", "#1c1b1f", "#2a2421")
W, H, PAD = 460, 548, 16
PHOTO_H = 214

CARDS = [
    dict(slug="publication-ai-rca", photo="img/projects/vm-investigations.webp",
         title="AI that automates root-cause analysis for VM downtime",
         body="How AI and MCP turn Azure telemetry into a recovery timeline and a structured root-cause report, attached directly to the incident.",
         label="Published on Microsoft's Azure blog", button="Read the article"),
    dict(slug="publication-vm-recovery", photo="img/projects/vm-recovery.webp",
         title="Automated VM recovery that minimizes downtime",
         body="A three-stage detect, diagnose and mitigate approach to recovering Azure virtual machines automatically and minimizing customer downtime.",
         label="Published on Microsoft's Azure blog", button="Read the article"),
    dict(slug="publication-private-cloud", photo="img/projects/openstack-cloud.webp",
         title="Building an OpenStack private cloud",
         body="Research on designing and building a private cloud on OpenStack, from my computer science studies at the University of the Basque Country.",
         label="Research · Google Scholar", button="Read the research"),
    dict(slug="publication-spoofing", photo=None, panel=("Investigación", "2020 · in Spanish"),
         title="Database integration to detect spoofing attacks",
         body="Research, written in Spanish, on integrating databases to detect spoofing attacks. Original title: Integración de bases de datos para la detección de ataques mediante Spoofing.",
         label="Research · Google Scholar", button="Read the research"),
]


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()


def photo_b64(rel: str) -> str:
    im = Image.open(PORTFOLIO / rel).convert("RGB")
    im = im.resize((int((W - 2 * PAD) * 2), int(PHOTO_H * 2)), Image.LANCZOS)   # 2x for retina
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=76, optimize=True, progressive=True)
    return base64.b64encode(buf.getvalue()).decode()


def wrap(text: str, max_chars: int, max_lines: int) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if len(trial) <= max_chars or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    lines.append(line)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(".,:;") + "…"
    return lines


def render(card: dict, fonts_css: str) -> str:
    esc = lambda s: html.escape(s, quote=False)
    pw, ph = W - 2 * PAD, PHOTO_H
    if card.get("photo"):
        media = (f'<image href="data:image/jpeg;base64,{photo_b64(card["photo"])}" x="{PAD}" y="{PAD}" width="{pw}" height="{ph}" '
                 f'preserveAspectRatio="xMidYMid slice" clip-path="url(#ph)"/>')
    else:
        big, small = card["panel"]
        media = (f'<rect x="{PAD}" y="{PAD}" width="{pw}" height="{ph}" rx="16" fill="{PANEL}"/>'
                 f'<text x="{PAD + 28}" y="{PAD + ph / 2 + 6}" font-family="Georgia, serif" font-style="italic" font-size="40" fill="{LABEL}">{esc(big)}</text>'
                 f'<text x="{PAD + 30}" y="{PAD + ph / 2 + 38}" class="mono" fill="#8f877c">{esc(small.upper())}</text>')
    y = PAD + ph + 44
    parts = [media]
    for line in wrap(card["title"], 31, 2):
        parts.append(f'<text x="{PAD + 10}" y="{y}" class="title">{esc(line)}</text>')
        y += 30
    y += 4
    for line in wrap(card["body"], 50, 4):
        parts.append(f'<text x="{PAD + 10}" y="{y}" class="body">{esc(line)}</text>')
        y += 23
    parts.append(f'<text x="{PAD + 10}" y="{y + 18}" class="mono">{esc(card["label"].upper())}</text>')
    label = f'{card["button"]}  ↗'
    bw = len(label) * 8.3 + 44
    bx, by = W - PAD - 10 - bw, H - PAD - 10 - 46
    parts.append(f'<rect x="{bx:.1f}" y="{by}" width="{bw:.1f}" height="46" rx="23" fill="{PILL}"/>'
                 f'<text x="{bx + bw / 2:.1f}" y="{by + 29}" text-anchor="middle" class="pill">{esc(label)}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(card["title"])}">'
            f'<defs><clipPath id="ph"><rect x="{PAD}" y="{PAD}" width="{pw}" height="{ph}" rx="16"/></clipPath></defs>'
            f'<style>{fonts_css}'
            f'.title{{font:600 23px Geist,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;fill:{TITLE};letter-spacing:-.2px}}'
            f'.body{{font:400 15px Geist,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;fill:{BODY}}}'
            f'.mono{{font:500 11.5px "Geist Mono",Menlo,Consolas,monospace;fill:{LABEL};letter-spacing:.9px}}'
            f'.pill{{font:500 14.5px Geist,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;fill:{PILL_TEXT}}}</style>'
            f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="24" fill="{CARD}" stroke="{EDGE}"/>'
            f'{"".join(parts)}</svg>\n')


def main() -> None:
    fonts_css = (f'@font-face{{font-family:Geist;src:url(data:font/woff2;base64,{b64(FONT_SANS)}) format("woff2");font-weight:100 900}}'
                 f'@font-face{{font-family:"Geist Mono";src:url(data:font/woff2;base64,{b64(FONT_MONO)}) format("woff2");font-weight:100 900}}')
    OUT.mkdir(parents=True, exist_ok=True)
    for card in CARDS:
        (OUT / f"{card['slug']}.svg").write_text(render(card, fonts_css), encoding="utf-8")
    print(f"wrote {len(CARDS)} cards to {OUT}")


if __name__ == "__main__":
    main()
