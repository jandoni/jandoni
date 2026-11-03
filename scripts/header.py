#!/usr/bin/env python3
"""Animated profile header: the Chicago skyline photo with the headline appearing
word by word and the title typing out. SVG + SMIL, so it plays inside GitHub's
<img> and stays sharp. Run `python scripts/header.py <skyline.png>` to rebuild.
"""

from __future__ import annotations

import base64
import io
import sys
from pathlib import Path

from PIL import Image

OUT = Path(__file__).resolve().parent.parent / "assets" / "header.svg"
INK, COPPER, MUTED = "#111111", "#8a4f28", "#5f5a54"
W, H, PHOTO_W = 1100, 260, 344
WORDS = [[("Building", INK, ""), ("cloud", INK, ""), ("and", INK, ""), ("AI", COPPER, ""), ("products", COPPER, "")],
         [("people", INK, ""), ("actually", INK, "i"), ("use.", INK, "")]]
ROLE = "Technical Program Manager, Cloud Reliability"   # the Director variant is kept as assets/header.svg


def photo_b64(src: str) -> str:
    im = Image.open(src).convert("RGB")
    crop = im.crop((2120, 0, im.width, im.height))          # skyline half of the banner, no text
    crop = crop.resize((PHOTO_W * 3, H * 3), Image.LANCZOS)  # 3x for sharp retina rendering
    buf = io.BytesIO()
    crop.save(buf, "JPEG", quality=78, optimize=True, progressive=True)
    return base64.b64encode(buf.getvalue()).decode()


def render(src: str, role: str = ROLE) -> str:
    b64 = photo_b64(src)
    parts = [
        '<defs>'
        '<linearGradient id="pg" x1="0" x2="1"><stop offset="0" stop-color="#e8e5e1"/><stop offset="1" stop-color="#dfddd7"/></linearGradient>'
        '<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#e3e0dc"/><stop offset="1" stop-color="#e3e0dc" stop-opacity="0"/></linearGradient>'
        f'<clipPath id="r"><rect width="{W}" height="{H}" rx="10"/></clipPath>'
        '</defs>',
        '<style>.w{font:46px Georgia,"Times New Roman",serif}.r{font:15px -apple-system,"Segoe UI",Helvetica,Arial,sans-serif}'
        '@media (prefers-reduced-motion: reduce){*{animation:none}}</style>',
        f'<g clip-path="url(#r)"><rect width="{W}" height="{H}" fill="url(#pg)"/>'
        f'<image href="data:image/jpeg;base64,{b64}" x="{W - PHOTO_W}" y="0" width="{PHOTO_W}" height="{H}" preserveAspectRatio="xMidYMax slice" opacity="0">'
        '<animate attributeName="opacity" from="0" to="1" begin="0s" dur="1.4s" fill="freeze"/></image>'
        f'<rect x="{W - PHOTO_W}" y="0" width="90" height="{H}" fill="url(#fade)"/></g>',
    ]
    # Type the headline one character at a time, like the title line below it.
    t, per_char = 0.6, 0.05
    for line, y in zip(WORDS, (112, 166)):
        spans = []
        for wi, (word, colour, kind) in enumerate(line):
            italic = ' font-style="italic"' if kind == "i" else ""
            chars = word + (" " if wi < len(line) - 1 else "")
            for ch in chars:
                spans.append(f'<tspan fill="{colour}"{italic} opacity="0">{ch}<set attributeName="opacity" to="1" begin="{t:.2f}s"/></tspan>')
                t += per_char
        parts.append(f'<text class="w" x="60" y="{y}" xml:space="preserve">{"".join(spans)}</text>')
        t += 0.25
    n = len(role)
    steps = ";".join(f"{j * 7.6:.1f}" for j in range(n + 1))
    parts.append(f'<clipPath id="rc"><rect x="60" y="196" height="22" width="0">'
                 f'<animate attributeName="width" values="{steps}" calcMode="discrete" begin="{t + .3:.2f}s" dur="1.4s" fill="freeze"/></rect></clipPath>'
                 f'<g clip-path="url(#rc)"><text class="r" x="60" y="212" fill="{MUTED}">{role}</text></g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="Building cloud and AI products people actually use. {role}.">' + "".join(parts) + "</svg>\n")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("photo", help="banner image the skyline is cropped from")
    ap.add_argument("--role", default=ROLE, help="the line typed under the headline")
    ap.add_argument("--out", type=Path, default=OUT.with_name("header-tpm.svg"))
    a = ap.parse_args()
    a.out.write_text(render(a.photo, a.role), encoding="utf-8")
    print(f"wrote {a.out} ({a.out.stat().st_size // 1024} KB): {a.role}")
