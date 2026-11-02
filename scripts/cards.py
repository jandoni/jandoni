#!/usr/bin/env python3
"""Render the project and publication cards on the profile as SVG.

GitHub strips CSS from READMEs, so a "card component" has to be an image.
Content lives in CARDS below; run `python scripts/cards.py` after editing it.
"""

from __future__ import annotations

import html
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "cards"

PAPER, BORDER, INK, BODY, MUTED, COPPER = "#f4f1ec", "#d8d2c8", "#111111", "#3a3530", "#6b655e", "#8a4f28"
W, H, PAD = 440, 200, 26
SERIF = "Georgia, 'Times New Roman', serif"
SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"

CARDS = [
    # projects
    dict(slug="vigia", kicker="Python · ONNX · FastAPI", title="VIGÍA",
         body="Disaster detection for the cameras cities already have: published detectors behind one validator that decides which alarms reach a person.",
         note="First prize, IIE Young Engineers 2025", pill="Looking for maintainers"),
    dict(slug="explorar-espana", kicker="JavaScript · Google 3D Maps · AWS", title="Explorar España",
         body="A 3D map of 38 museums, shipyards, universities and technology centres in Spain's engineering network, built for the Instituto de la Ingeniería de España.",
         note="First IIE–AWS prize, 2025", pill="Looking for a new owner"),
    dict(slug="linkedin-daily-agent", kicker="Python · n8n · Claude", title="LinkedIn daily agent",
         body="Finds tech news, drafts a post in my voice with the article's real numbers, renders the image, and waits in Telegram until I tap Publish.",
         note="Official LinkedIn API only", pill="MIT"),
    dict(slug="home-lab", kicker="Home Assistant · Proxmox · Python", title="Home lab",
         body="One mini PC running Home Assistant and a dozen services. A local voice assistant runs on the Intel iGPU, with Echo Shows reflashed as voice satellites.",
         note="Speech-to-text in 0.27 s, fully local", pill="Private"),
    # publications
    dict(slug="pub-ai-rca", kicker="Microsoft Tech Community · Azure Compute Blog",
         title="AI-Powered Downtime Investigation for Azure VMs: Automating Root Cause Analysis",
         body="How we use AI to investigate Azure VM downtime and draft the root cause automatically.",
         note="April 2026 · with five co-authors", pill="Article"),
    dict(slug="pub-vm-recovery", kicker="Microsoft Tech Community · Azure Compute Blog",
         title="Azure Automated Virtual Machine Recovery: Minimizing Downtime",
         body="How Azure spots virtual machines in trouble and recovers them automatically to cut downtime.",
         note="February 2026 · with eight co-authors", pill="Article"),
    dict(slug="pub-private-cloud", kicker="Research · University of the Basque Country",
         title="Design and build of a custom private cloud",
         body="Choosing how to build a private cloud, then designing and deploying it on OpenStack: the architecture, the trade-offs and the result.",
         note="2025 · Google Scholar", pill="Research"),
    dict(slug="pub-spoofing", kicker="Research · in Spanish",
         title="Integración de bases de datos para la detección de ataques mediante Spoofing",
         body="Integrating databases to detect spoofing attacks.",
         note="2020 · Google Scholar", pill="Research"),
]


def wrap(text: str, max_px: float, char_px: float) -> list[str]:
    """Greedy word wrap using an average character width."""
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if len(trial) * char_px <= max_px or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def render(card: dict) -> str:
    inner = W - 2 * PAD
    esc = html.escape
    # Title: one line at 22px if it fits, otherwise two lines at 17px.
    if len(card["title"]) * 10.4 <= inner:
        t_size, t_lines = 22, [card["title"]]
    else:
        t_size = 17
        t_lines = wrap(card["title"], inner, 8.3)[:2]
    y = 44
    parts = [f'<text x="{PAD}" y="{y}" class="k">{esc(card["kicker"])}</text>']
    y += 14 + t_size
    for line in t_lines:
        parts.append(f'<text x="{PAD}" y="{y}" class="t" font-size="{t_size}">{esc(line)}</text>')
        y += t_size + 5
    y += 6
    max_body = 3 if len(t_lines) == 1 else 2
    body = wrap(card["body"], inner, 6.55)
    if len(body) > max_body:
        body = body[:max_body]
        body[-1] = body[-1].rstrip(".,") + "…"
    for line in body:
        parts.append(f'<text x="{PAD}" y="{y}" class="b">{esc(line)}</text>')
        y += 19
    # Footer: copper note on the left, outlined pill on the right.
    fy = H - 24
    parts.append(f'<text x="{PAD}" y="{fy}" class="n">{esc(card["note"])}</text>')
    pill = card["pill"]
    pw = len(pill) * 6.4 + 22
    px = W - PAD - pw
    parts.append(f'<rect x="{px:.1f}" y="{fy - 15}" width="{pw:.1f}" height="22" rx="11" fill="none" stroke="{COPPER}" stroke-width="1"/>')
    parts.append(f'<text x="{px + pw / 2:.1f}" y="{fy}" class="p" text-anchor="middle">{esc(pill)}</text>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(card['title'])}">
<style>
  .k {{ font: 400 12px {SANS}; fill: {MUTED}; }}
  .t {{ font-family: {SERIF}; font-weight: 400; fill: {INK}; }}
  .b {{ font: 400 13.5px {SANS}; fill: {BODY}; }}
  .n {{ font: 400 12.5px {SANS}; fill: {COPPER}; }}
  .p {{ font: 500 11.5px {SANS}; fill: {COPPER}; }}
</style>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8" fill="{PAPER}" stroke="{BORDER}"/>
{chr(10).join(parts)}
</svg>
"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for card in CARDS:
        (OUT / f"{card['slug']}.svg").write_text(render(card), encoding="utf-8")
    print(f"wrote {len(CARDS)} cards to {OUT}")


if __name__ == "__main__":
    main()
