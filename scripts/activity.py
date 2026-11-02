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


def render(days: list[tuple[dt.date, int]]) -> str:
    days = sorted(days)
    total = sum(n for _, n in days)
    active = sum(1 for _, n in days if n)
    streak = longest_streak(days)
    by_month: dict[tuple[int, int], int] = {}
    for d, n in days:
        by_month[(d.year, d.month)] = by_month.get((d.year, d.month), 0) + n
    (by, bm), _ = max(by_month.items(), key=lambda kv: kv[1])
    busiest = dt.date(by, bm, 1).strftime("%B %Y")

    nonzero = sorted(n for _, n in days if n)
    cuts = [nonzero[int(len(nonzero) * q)] for q in (0.25, 0.5, 0.75)] if nonzero else [1, 2, 3]

    cell, gap = 11, 3
    left, top = 40, 92
    first = days[0][0]
    start = first - dt.timedelta(days=(first.weekday() + 1) % 7)   # weeks start on Sunday
    rects, months = [], []
    last_month = None
    for d, n in days:
        col = (d - start).days // 7
        row = (d.weekday() + 1) % 7
        x, y = left + col * (cell + gap), top + row * (cell + gap)
        rects.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" '
                     f'fill="{LEVELS[level(n, cuts)]}"><title>{n} on {d.isoformat()}</title></rect>')
        if d.day <= 7 and row == 0 and d.month != last_month:
            months.append(f'<text x="{x}" y="{top - 8}" class="m">{d.strftime("%b")}</text>')
            last_month = d.month
    weeks = (days[-1][0] - start).days // 7 + 1
    width = left + weeks * (cell + gap) + 28
    height = top + 7 * (cell + gap) + 44
    legend_x = width - 28 - 5 * (cell + gap) - 70
    legend = "".join(
        f'<rect x="{legend_x + 34 + i * (cell + gap)}" y="{height - 30}" width="{cell}" height="{cell}" rx="2" fill="{c}"/>'
        for i, c in enumerate(LEVELS))
    updated = dt.date.today().strftime("%-d %B %Y")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{total} GitHub contributions in the last year">
<style>
  .t {{ font: 400 22px Georgia, 'Times New Roman', serif; fill: {INK}; }}
  .n {{ fill: {COPPER}; }}
  .s {{ font: 400 12.5px -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif; fill: {MUTED}; }}
  .m {{ font: 400 10.5px -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif; fill: {MUTED}; }}
</style>
<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="8" fill="{PAPER}" stroke="{BORDER}"/>
<text x="{left}" y="42" class="t"><tspan class="n">{total:,}</tspan> contributions in the last year</text>
<text x="{left}" y="64" class="s">{active} active days · longest streak {streak} days · busiest month {busiest} · private work counted, not shown</text>
{''.join(months)}
{''.join(rects)}
<text x="{left}" y="{height - 21}" class="m">Updated {updated}</text>
<text x="{legend_x}" y="{height - 21}" class="m">Less</text>{legend}<text x="{legend_x + 34 + 5 * (cell + gap) + 4}" y="{height - 21}" class="m">More</text>
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
