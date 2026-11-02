#!/usr/bin/env python3
"""A short terminal session for the profile README, typed out with SMIL so it
animates inside GitHub's <img>. Edit SESSION and run `python scripts/terminal.py`.
Pass --dark for a dark card.
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "terminal.svg"
PROMPT = "jon@chicago ~ $ "
SESSION = [
    ("whoami", ["Director of Product Management, Platform Engineering"]),
    ("cat career.txt", ["SRE for live TV broadcasting, Bilbao",
                        "Data infrastructure behind a 500 TB data lake on AWS, Chicago",
                        "Reliability and capacity programs for Azure's VM fleet, Microsoft"]),
    ("ls building/", ["vigia   explorar-espana   linkedin-daily-agent",
                      "casa-voice-assistant   self-hosted-homelab   echo-show-home-assistant"]),
]
MONO = "Menlo, 'SF Mono', Consolas, 'DejaVu Sans Mono', monospace"
CW, LH, FS = 8.1, 21, 13.5          # char width, line height, font size
TYPE_S, PAUSE_S = 0.045, 0.35        # per character, between steps

PALETTES = {
    "paper": dict(bg="#f4f1ec", border="#d8d2c8", bar="#ebe6de", prompt="#8a4f28", cmd="#111111", out="#4a453f", title="#6b655e"),
    "dark": dict(bg="#16120f", border="#3a2f27", bar="#201a16", prompt="#c08250", cmd="#f1ebe3", out="#bdb3a7", title="#8c8277"),
}


def render(palette: str) -> str:
    c = PALETTES[palette]
    esc = lambda s: html.escape(s, quote=False)
    x0, y, t = 24, 64, 0.6
    parts, cid = [], 0
    longest = max([len(PROMPT) + len(cmd) for cmd, _ in SESSION] + [len(o) for _, outs in SESSION for o in outs])
    width = round(x0 * 2 + longest * CW + 10)
    for cmd, outs in SESSION:
        # prompt appears, then the command types out
        parts.append(f'<text x="{x0}" y="{y}" fill="{c["prompt"]}" opacity="0">{esc(PROMPT)}'
                     f'<set attributeName="opacity" to="1" begin="{t:.2f}s"/></text>')
        cx = x0 + len(PROMPT) * CW
        steps = ";".join(f"{i * CW:.1f}" for i in range(len(cmd) + 1))
        dur = len(cmd) * TYPE_S
        parts.append(f'<clipPath id="k{cid}"><rect x="{cx:.1f}" y="{y - 15}" height="20" width="0">'
                     f'<animate attributeName="width" values="{steps}" calcMode="discrete" begin="{t:.2f}s" dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>'
                     f'<text x="{cx:.1f}" y="{y}" fill="{c["cmd"]}" clip-path="url(#k{cid})">{esc(cmd)}</text>')
        cid += 1
        t += dur + PAUSE_S
        for line in outs:                      # output lines appear one by one
            y += LH
            parts.append(f'<text x="{x0}" y="{y}" fill="{c["out"]}" opacity="0">{esc(line)}'
                         f'<set attributeName="opacity" to="1" begin="{t:.2f}s"/></text>')
            t += 0.12
        y += LH
        t += PAUSE_S
    # final prompt with a blinking cursor
    parts.append(f'<text x="{x0}" y="{y}" fill="{c["prompt"]}" opacity="0">{esc(PROMPT)}<set attributeName="opacity" to="1" begin="{t:.2f}s"/></text>')
    parts.append(f'<rect x="{x0 + len(PROMPT) * CW:.1f}" y="{y - 13}" width="{CW:.1f}" height="16" fill="{c["prompt"]}" opacity="0">'
                 f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1.1s" begin="{t:.2f}s" repeatCount="indefinite"/></rect>')
    height = round(y + 26)
    bar = (f'<rect x=".5" y=".5" width="{width - 1}" height="30" rx="8" fill="{c["bar"]}"/>'
           f'<rect x=".5" y="22" width="{width - 1}" height="9" fill="{c["bar"]}"/>'
           f'<line x1="0" y1="31" x2="{width}" y2="31" stroke="{c["border"]}"/>'
           f'<text x="{width / 2:.0f}" y="20" text-anchor="middle" fill="{c["title"]}" style="font:12px -apple-system,\'Segoe UI\',Helvetica,Arial,sans-serif">jon@chicago: ~</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" '
            f'aria-label="Terminal: whoami, Director of Product Management, Platform Engineering. Career: SRE, data infrastructure, Azure reliability. Building: VIGIA, Explorar Espana, LinkedIn daily agent, Casa voice assistant, self-hosted homelab, Echo Show for Home Assistant.">'
            f'<style>text{{font:{FS}px {MONO};white-space:pre}}@media (prefers-reduced-motion: reduce){{*{{animation:none}}}}</style>'
            f'<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="8" fill="{c["bg"]}" stroke="{c["border"]}"/>'
            f'{bar}{"".join(parts)}</svg>\n')


if __name__ == "__main__":
    pal = "dark" if "--dark" in sys.argv else "paper"
    OUT.write_text(render(pal), encoding="utf-8")
    print(f"wrote {OUT} ({pal})")
