#!/usr/bin/env python3
"""Draw the last year of GitHub contributions as an SVG in the profile palette.

Reads the same public contribution calendar GitHub shows on the profile page
(private work appears there as counts only, never as names), so the card
needs no personal token: the Actions GITHUB_TOKEN is enough. Falls back to the
public calendar HTML if the API call fails.

    python scripts/activity.py jandoni assets/activity.svg
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
import urllib.request

PAPER = "#f4f1ec"
BORDER = "#d8d2c8"
INK = "#111111"
MUTED = "#6b655e"
COPPER = "#8a4f28"
LEVELS = ["#e4ded4", "#e3c5aa", "#cf9b70", "#ad6c3d", "#7d4421"]

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def from_api(login: str) -> list[tuple[dt.date, int]]:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("no GITHUB_TOKEN")
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [(dt.date.fromisoformat(d["date"]), d["contributionCount"])
            for w in weeks for d in w["contributionDays"]]


def from_html(login: str) -> list[tuple[dt.date, int]]:
    url = f"https://github.com/users/{login}/contributions"
    with urllib.request.urlopen(url, timeout=30) as resp:
        html = resp.read().decode()
    cells = {}
    for tag in re.findall(r"<td[^>]*ContributionCalendar-day[^>]*>", html):
        cid, date = re.search(r'id="([^"]+)"', tag), re.search(r'data-date="([^"]+)"', tag)
        if cid and date:
            cells[cid.group(1)] = date.group(1)
    days = []
    for cell_id, count in re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]+)</tool-tip>', html):
        if cell_id in cells:
            m = re.match(r"(\d+) contribution", count)
            days.append((dt.date.fromisoformat(cells[cell_id]), int(m.group(1)) if m else 0))
    if not days:
        raise RuntimeError("could not parse the public calendar")
    return sorted(days)


def level(count: int, cuts: list[int]) -> int:
    if count == 0:
        return 0
    return 1 + sum(count > c for c in cuts)


def longest_streak(days: list[tuple[dt.date, int]]) -> int:
    best = run = 0
    for _, n in days:
        run = run + 1 if n else 0
        best = max(best, run)
    return best


PLANE = "M0,0 L14,5 L0,10 L3,5 Z"   # a paper plane, pointing right


def render(days: list[tuple[dt.date, int]]) -> str:
    """A compact, animated card: cells fill in week by week, then a paper plane
    glides across the year and the busiest days light up as it passes. Plays once
    per page load and stays still for visitors who prefer reduced motion."""
    days = sorted(days)
    total = sum(n for _, n in days)
    active = sum(1 for _, n in days if n)
    streak = longest_streak(days)
    by_month: dict[tuple[int, int], int] = {}
    for d, n in days:
        by_month[(d.year, d.month)] = by_month.get((d.year, d.month), 0) + n
    (by, bm), _ = max(by_month.items(), key=lambda kv: kv[1])
    busiest = dt.date(by, bm, 1).strftime("%b %Y")

    nonzero = sorted(n for _, n in days if n)
    cuts = [nonzero[int(len(nonzero) * q)] for q in (0.25, 0.5, 0.75)] if nonzero else [1, 2, 3]
    top_days = {d for d, n in sorted(days, key=lambda x: -x[1])[:8] if n}

    cell, gap = 9, 2.6
    step = cell + gap
    left, top = 22, 80
    first = days[0][0]
    start = first - dt.timedelta(days=(first.weekday() + 1) % 7)
    weeks = (days[-1][0] - start).days // 7 + 1
    width = round(left * 2 + weeks * step - gap)
    height = top + 7 * step + 34
    fill_s, fly_s, fly_delay = 1.6, 3.2, 1.8          # seconds
    rects, months, glows = [], [], []
    last_month = None
    for d, n in days:
        col = (d - start).days // 7
        row = (d.weekday() + 1) % 7
        x, y = left + col * step, top + row * step
        delay = fill_s * col / max(weeks - 1, 1)
        rects.append(f'<rect class="c" style="animation-delay:{delay:.2f}s" x="{x:.1f}" y="{y:.1f}" '
                     f'width="{cell}" height="{cell}" rx="1.6" fill="{LEVELS[level(n, cuts)]}"/>')
        if d in top_days:
            pass_at = fly_delay + fly_s * col / max(weeks - 1, 1)
            glows.append(f'<rect class="g" style="animation-delay:{pass_at:.2f}s" x="{x - 2:.1f}" y="{y - 2:.1f}" '
                         f'width="{cell + 4}" height="{cell + 4}" rx="3" fill="none" stroke="{COPPER}" stroke-width="1.4"/>')
        if d.day <= 7 and row == 0 and d.month != last_month:
            months.append(f'<text x="{x:.1f}" y="{top - 7}" class="m">{d.strftime("%b")}</text>')
            last_month = d.month
    plane_y = 45
    travel = weeks * step + 10
    updated = dt.date.today().strftime("%-d %b %Y")
    legend_x = width - left - 5 * step - 58
    legend = "".join(f'<rect x="{legend_x + 28 + i * step:.1f}" y="{height - 23}" width="{cell}" height="{cell}" rx="1.6" fill="{c}"/>'
                     for i, c in enumerate(LEVELS))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{total} GitHub contributions in the last year">
<style>
  .t {{ font: 400 20px Georgia, 'Times New Roman', serif; fill: {INK}; }}
  .n {{ fill: {COPPER}; }}
  .s {{ font: 400 11.5px -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif; fill: {MUTED}; }}
  .m {{ font: 400 9.5px -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif; fill: {MUTED}; }}
  .c {{ opacity: 0; animation: in .35s ease-out forwards; }}
  .g {{ opacity: 0; animation: glow 1.1s ease-out forwards; }}
  .p {{ opacity: 0; animation: fly {fly_s}s cubic-bezier(.45,.05,.4,1) {fly_delay}s forwards; }}
  @keyframes in {{ to {{ opacity: 1; }} }}
  @keyframes glow {{ 0% {{ opacity: 0; }} 30% {{ opacity: 1; }} 100% {{ opacity: .55; }} }}
  @keyframes fly {{
    0% {{ opacity: 0; transform: translate(0px, 6px); }}
    8% {{ opacity: 1; }}
    50% {{ transform: translate({travel / 2:.0f}px, -2px); }}
    92% {{ opacity: 1; }}
    100% {{ opacity: 0; transform: translate({travel:.0f}px, 4px); }}
  }}
  @media (prefers-reduced-motion: reduce) {{
    .c, .g {{ animation: none; opacity: 1; }}
    .g {{ opacity: .55; }}
    .p {{ display: none; }}
  }}
</style>
<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="8" fill="{PAPER}" stroke="{BORDER}"/>
<text x="{left}" y="34" class="t"><tspan class="n">{total:,}</tspan> contributions in the last year</text>
{''.join(months)}
{''.join(rects)}
{''.join(glows)}
<g class="p"><path d="{PLANE}" transform="translate({left - 14},{plane_y})" fill="{COPPER}"/></g>
<text x="{left}" y="{height - 15}" class="m">Updated {updated} · private work counted, not shown</text>
<text x="{legend_x}" y="{height - 15}" class="m">Less</text>{legend}<text x="{legend_x + 28 + 5 * step + 3:.1f}" y="{height - 15}" class="m">More</text>
</svg>
"""


def main() -> int:
    login, out = sys.argv[1], sys.argv[2]
    try:
        days = from_api(login)
    except Exception as exc:  # network, auth or schema change: use the public page
        print(f"API unavailable ({exc}); reading the public calendar", file=sys.stderr)
        days = from_html(login)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(render(days))
    print(f"{out}: {sum(n for _, n in days)} contributions over {len(days)} days")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
