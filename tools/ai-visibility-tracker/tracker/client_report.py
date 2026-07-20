"""Generates printable/emailable reports for one client's latest run —
Markdown (house style matches reports/page-review-template.md) and a
self-contained HTML version (single file, logo embedded as base64, opens in
any browser and prints/exports to PDF cleanly — the more reliable format for
actually emailing to a client, since plain .md doesn't render images or
tables in most mail clients).
"""

import base64
import datetime
import html as html_lib
import os

from . import citability, competitors, db
from .config import CLIENTS_DIR, load_client_config
from .platforms import ALL as ALL_PLATFORMS
from .runner import REPLICATES_PER_PROMPT

PLATFORM_NAMES = [p.NAME for p in ALL_PLATFORMS]
PLATFORM_LABELS = {"chatgpt": "ChatGPT", "perplexity": "Perplexity", "gemini": "Gemini"}

LOGO_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "citability-index-logo.png")

METHODOLOGY_DISCLAIMER = (
    "CI results are pulled from providers' grounded APIs, not the consumer-facing "
    "apps (chatgpt.com, gemini.google.com, etc.). Consumer apps can differ in model "
    "version, system instructions, personalization, and rollout state. The "
    "Citability Index is a reproducible directional benchmark — it shows trend "
    "and relative gap versus competitors, not a guarantee of what any individual "
    "end-user will see in a live chat session."
)


def _cell_stats(rows):
    """rows: the replicate rows for one (prompt, platform) cell — 0 if that
    platform wasn't tested, otherwise REPLICATES_PER_PROMPT of them. Returns
    (label, kind) where kind is 'cited' / 'mentioned' / 'none' / 'skipped'."""
    if not rows:
        return "not tested", "skipped"
    n = len(rows)
    cited_n = sum(1 for r in rows if r["cited"])
    mentioned_n = sum(1 for r in rows if r["mentioned"])
    if cited_n:
        return f"Cited {cited_n}/{n}", "cited"
    if mentioned_n:
        return f"Mentioned {mentioned_n}/{n}", "mentioned"
    return f"— 0/{n}", "none"


def _gather(client_slug):
    """All the data a report needs, computed once — markdown and HTML render
    from this same dict instead of duplicating DB/scoring calls."""
    cfg = load_client_config(client_slug)
    if cfg is None:
        raise ValueError(f"No config at clients/{client_slug}/ai-visibility-tracker.json")

    conn = db.connect()
    latest, previous, flagged, delta = citability.compare_to_previous(conn, cfg.client, PLATFORM_NAMES)
    if latest is None:
        conn.close()
        raise ValueError(f"No runs stored yet for {cfg.client} — run.py --run needs to complete first.")

    top_domains = competitors.top_competing_domains(conn, cfg.client, latest["timestamp"], cfg.domain)
    matrix = db.prompt_matrix(conn, cfg.client, latest["timestamp"])
    rec_gaps = citability.recommendation_gaps(conn, cfg.client, latest["timestamp"])
    conn.close()

    band = latest["band"]
    return {
        "cfg": cfg,
        "today": datetime.date.today().isoformat(),
        "latest": latest,
        "previous": previous,
        "flagged": flagged,
        "delta": delta,
        "top_domains": top_domains,
        "matrix": matrix,
        "rec_gaps": rec_gaps,
        "blended": latest["blended"],
        "band": band,
        "band_desc": citability.BAND_DESCRIPTIONS.get(band, ""),
    }


def _trend_sentence(data):
    if data["previous"] is None:
        return ""
    direction = "up" if data["delta"] > 0 else ("down" if data["delta"] < 0 else "unchanged")
    sentence = (f" That's {direction} {abs(data['delta']):.1f} points since the previous run "
                f"on {data['previous']['timestamp'][:10]}.")
    if data["flagged"]:
        sentence += " This drop is significant enough to flag directly."
    return sentence


# ---------------------------------------------------------------- Markdown

def _render_markdown(data):
    cfg = data["cfg"]
    matrix = data["matrix"]
    blended = data["blended"]
    band = data["band"]
    band_desc = data["band_desc"]

    lines = []
    lines.append(f"# AI Visibility Report — {cfg.client}")
    lines.append(f"**Client:** {cfg.client} | **Date:** {data['today']} | **Prepared by:** Small Factory 5")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Summary")
    lines.append(
        f"{cfg.client}'s blended Citability Index is **{blended['citability_index']} ({band})** "
        f"across {len(matrix)} tracked prompt(s) on {', '.join(PLATFORM_LABELS[p] for p in PLATFORM_NAMES)}."
        f"{_trend_sentence(data)} {band_desc}"
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Citability Index")
    lines.append("")
    lines.append(f"**Blended: {blended['citability_index']} ({band})**")
    lines.append("")
    lines.append("| Platform | Citability Index | Mention Rate | Citation Rate | Recommendation Rate | Prompts Tested |")
    lines.append("|---|---|---|---|---|---|")
    for platform in PLATFORM_NAMES:
        idx = data["latest"]["per_platform"][platform]
        label = PLATFORM_LABELS[platform]
        if idx["n"] == 0:
            lines.append(f"| {label} | — | — | — | — | not tested (no API key set) |")
        else:
            lines.append(
                f"| {label} | {idx['citability_index']} | {idx['mention_rate']*100:.0f}% "
                f"| {idx['citation_rate']*100:.0f}% | {idx['recommendation_rate']*100:.0f}% | {idx['n']} |"
            )
    lines.append("")
    lines.append(
        "*Recommendation Rate is reported alongside the Citability Index, not blended into it — "
        "it measures how often the AI singled the brand out as the pick, not just named it "
        "alongside others.*"
    )
    lines.append("")
    if data["previous"] is not None:
        arrow = "up" if data["delta"] > 0 else ("down" if data["delta"] < 0 else "flat")
        flag_note = " — **flagged**" if data["flagged"] else ""
        lines.append(f"**Trend:** {arrow} {data['delta']:+.1f} vs. previous run "
                      f"({data['previous']['timestamp'][:10]}){flag_note}")
    else:
        lines.append("**Trend:** first tracked run — no prior data yet.")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Who's Getting Cited Instead")
    if data["top_domains"]:
        lines.append(f"*(Other domains appearing as sources across {cfg.client}'s tracked prompts this run.)*")
        lines.append("")
        lines.append("| Domain | Times Cited | Example Prompt |")
        lines.append("|---|---|---|")
        for d in data["top_domains"]:
            lines.append(f"| {d['domain']} | {d['count']} | “{d['example_prompt']}” |")
    else:
        lines.append(f"No competing domains were cited across {cfg.client}'s tracked prompts this run.")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Recommendation Gaps")
    if data["rec_gaps"]:
        lines.append(
            f"*(Prompts where {cfg.client} was named or cited but not the AI's explicit pick — "
            f"the most actionable finding here: present in the answer, losing the recommendation.)*"
        )
        lines.append("")
        lines.append("| Prompt | Platform |")
        lines.append("|---|---|")
        for gap in data["rec_gaps"]:
            lines.append(f"| {gap['prompt']} | {PLATFORM_LABELS.get(gap['platform'], gap['platform'])} |")
    else:
        lines.append(f"No gap cases this run — every prompt where {cfg.client} appeared, it was also the "
                      f"recommendation (or no responses were classified).")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Prompts Tracked")
    lines.append(f"*(Each prompt is run {REPLICATES_PER_PROMPT} times per platform per report — cells show "
                  f"how many of those {REPLICATES_PER_PROMPT} calls surfaced a citation or mention, not a "
                  f"single pass/fail.)*")
    lines.append("")
    header = "| Prompt | " + " | ".join(PLATFORM_LABELS[p] for p in PLATFORM_NAMES) + " |"
    sep = "|---|" + "|".join(["---"] * len(PLATFORM_NAMES)) + "|"
    lines.append(header)
    lines.append(sep)
    for prompt, by_platform in matrix.items():
        cells = []
        for p in PLATFORM_NAMES:
            label, kind = _cell_stats(by_platform.get(p))
            cells.append(f"**{label}**" if kind == "cited" else label)
        lines.append(f"| {prompt} | {' | '.join(cells)} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## What This Means")
    lines.append(f"{band_desc}")
    lines.append("")
    lines.append(
        "*Citability Index = (Mention Rate × 40) + (Citation Rate × 60). "
        "Citation is weighted higher than mention because being cited as a source "
        "means the page itself is doing the work, not just brand-name recognition.*"
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Methodology Note")
    lines.append(METHODOLOGY_DISCLAIMER)
    lines.append("")

    return "\n".join(lines)


def generate_markdown(client_slug):
    return _render_markdown(_gather(client_slug))


def save_report(client_slug):
    markdown = generate_markdown(client_slug)
    reports_dir = os.path.join(CLIENTS_DIR, client_slug, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    today = datetime.date.today().isoformat()
    # Client slug in the filename too, not just the parent folder — so a report
    # stays self-identifying once it's pulled out of clients/<slug>/reports/
    # (emailed as an attachment, dropped in a shared folder, etc.).
    path = os.path.join(reports_dir, f"{today}-{client_slug}-ai-visibility-report.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(markdown)
    return path


# -------------------------------------------------------------------- HTML

_HTML_STYLE = """
body{margin:0;background:#EDECE4;color:#15171B;font-family:-apple-system,'IBM Plex Sans',Arial,sans-serif;line-height:1.5;}
.wrap{max-width:820px;margin:0 auto;padding:40px 32px 64px;}
.logo{display:block;margin:0 auto 24px;width:120px;height:120px;}
h1{font-size:1.7rem;text-align:center;margin:0 0 6px;color:#15171B;}
.meta{text-align:center;color:#5B6472;font-size:0.9rem;margin-bottom:32px;}
h2{font-size:1.2rem;color:#2C4870;border-bottom:2px solid #2C4870;padding-bottom:6px;margin:36px 0 14px;}
.card{background:#fff;border:1px solid #C9C6BA;border-radius:6px;padding:24px 28px;margin-bottom:8px;}
.score{font-size:2.6rem;font-weight:800;color:#C15A2E;}
.band{font-size:1.1rem;color:#2C4870;font-weight:600;}
table{width:100%;border-collapse:collapse;margin:12px 0;background:#fff;}
th,td{text-align:left;padding:9px 12px;border:1px solid #C9C6BA;font-size:0.92rem;}
th{background:#2C4870;color:#fff;}
.note{color:#5B6472;font-size:0.88rem;font-style:italic;}
.trend-flagged{color:#B23A2E;font-weight:700;}
.cell-cited{color:#2E6B3E;font-weight:700;}
.cell-mentioned{color:#8A6D00;}
.cell-none{color:#8a8a8a;}
.cell-skipped{color:#b5b5b5;font-style:italic;}
.disclaimer{background:#fff;border-left:4px solid #C15A2E;padding:14px 20px;font-size:0.86rem;color:#5B6472;margin-top:8px;}
footer{text-align:center;color:#8a8a8a;font-size:0.78rem;margin-top:40px;}
"""

_CELL_CLASS = {"cited": "cell-cited", "mentioned": "cell-mentioned", "none": "cell-none", "skipped": "cell-skipped"}


def _e(text):
    return html_lib.escape(str(text))


def _logo_data_uri():
    if not os.path.exists(LOGO_PATH):
        return None
    with open(LOGO_PATH, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _render_html(data):
    cfg = data["cfg"]
    matrix = data["matrix"]
    blended = data["blended"]
    band = data["band"]
    band_desc = data["band_desc"]
    logo_uri = _logo_data_uri()

    parts = []
    parts.append(f"<!doctype html><html lang='en'><head><meta charset='utf-8'>")
    parts.append(f"<title>AI Visibility Report — {_e(cfg.client)}</title>")
    parts.append(f"<style>{_HTML_STYLE}</style></head><body><div class='wrap'>")

    if logo_uri:
        parts.append(f"<img class='logo' src='{logo_uri}' alt='Citability Index — Small Factory 5'>")
    parts.append(f"<h1>AI Visibility Report — {_e(cfg.client)}</h1>")
    parts.append(f"<div class='meta'>Client: {_e(cfg.client)} &nbsp;|&nbsp; Date: {_e(data['today'])} "
                  f"&nbsp;|&nbsp; Prepared by: Small Factory 5</div>")

    parts.append("<h2>Summary</h2><div class='card'>")
    parts.append(f"<p>{_e(cfg.client)}'s blended Citability Index is "
                  f"<span class='score'>{blended['citability_index']}</span> "
                  f"<span class='band'>({_e(band)})</span></p>")
    parts.append(f"<p>Across {len(matrix)} tracked prompt(s) on "
                  f"{_e(', '.join(PLATFORM_LABELS[p] for p in PLATFORM_NAMES))}."
                  f"{_e(_trend_sentence(data))}</p>")
    parts.append(f"<p>{_e(band_desc)}</p></div>")

    parts.append("<h2>Citability Index by Platform</h2>")
    parts.append("<table><tr><th>Platform</th><th>Citability Index</th><th>Mention Rate</th>"
                  "<th>Citation Rate</th><th>Recommendation Rate</th><th>Prompts Tested</th></tr>")
    for platform in PLATFORM_NAMES:
        idx = data["latest"]["per_platform"][platform]
        label = PLATFORM_LABELS[platform]
        if idx["n"] == 0:
            parts.append(f"<tr><td>{_e(label)}</td><td>—</td><td>—</td><td>—</td><td>—</td>"
                          f"<td>not tested (no API key set)</td></tr>")
        else:
            parts.append(
                f"<tr><td>{_e(label)}</td><td>{idx['citability_index']}</td>"
                f"<td>{idx['mention_rate']*100:.0f}%</td><td>{idx['citation_rate']*100:.0f}%</td>"
                f"<td>{idx['recommendation_rate']*100:.0f}%</td><td>{idx['n']}</td></tr>"
            )
    parts.append("</table>")
    parts.append("<p class='note'>Recommendation Rate is reported alongside the Citability Index, not "
                  "blended into it — it measures how often the AI singled the brand out as the pick, not "
                  "just named it alongside others.</p>")
    if data["previous"] is not None:
        arrow = "up" if data["delta"] > 0 else ("down" if data["delta"] < 0 else "flat")
        cls = " class='trend-flagged'" if data["flagged"] else ""
        flag_note = " — FLAGGED" if data["flagged"] else ""
        parts.append(f"<p{cls}>Trend: {arrow} {data['delta']:+.1f} vs. previous run "
                      f"({_e(data['previous']['timestamp'][:10])}){flag_note}</p>")
    else:
        parts.append("<p class='note'>First tracked run — no prior data yet.</p>")

    parts.append("<h2>Who's Getting Cited Instead</h2>")
    if data["top_domains"]:
        parts.append(f"<p class='note'>Other domains appearing as sources across "
                      f"{_e(cfg.client)}'s tracked prompts this run.</p>")
        parts.append("<table><tr><th>Domain</th><th>Times Cited</th><th>Example Prompt</th></tr>")
        for d in data["top_domains"]:
            parts.append(f"<tr><td>{_e(d['domain'])}</td><td>{d['count']}</td>"
                          f"<td>“{_e(d['example_prompt'])}”</td></tr>")
        parts.append("</table>")
    else:
        parts.append(f"<p>No competing domains were cited across {_e(cfg.client)}'s tracked prompts this run.</p>")

    parts.append("<h2>Recommendation Gaps</h2>")
    if data["rec_gaps"]:
        parts.append(f"<p class='note'>Prompts where {_e(cfg.client)} was named or cited but not the AI's "
                      f"explicit pick — the most actionable finding here: present in the answer, losing the "
                      f"recommendation.</p>")
        parts.append("<table><tr><th>Prompt</th><th>Platform</th></tr>")
        for gap in data["rec_gaps"]:
            parts.append(f"<tr><td>{_e(gap['prompt'])}</td>"
                          f"<td>{_e(PLATFORM_LABELS.get(gap['platform'], gap['platform']))}</td></tr>")
        parts.append("</table>")
    else:
        parts.append(f"<p>No gap cases this run — every prompt where {_e(cfg.client)} appeared, it was also "
                      f"the recommendation (or no responses were classified).</p>")

    parts.append("<h2>Prompts Tracked</h2>")
    parts.append(f"<p class='note'>Each prompt is run {REPLICATES_PER_PROMPT} times per platform per report — "
                  f"cells show how many of those {REPLICATES_PER_PROMPT} calls surfaced a citation or mention, "
                  f"not a single pass/fail.</p>")
    parts.append("<table><tr><th>Prompt</th>" + "".join(f"<th>{_e(PLATFORM_LABELS[p])}</th>" for p in PLATFORM_NAMES) + "</tr>")
    for prompt, by_platform in matrix.items():
        cells = []
        for p in PLATFORM_NAMES:
            label, kind = _cell_stats(by_platform.get(p))
            cells.append(f"<td class='{_CELL_CLASS[kind]}'>{_e(label)}</td>")
        parts.append(f"<tr><td>{_e(prompt)}</td>{''.join(cells)}</tr>")
    parts.append("</table>")

    parts.append("<h2>What This Means</h2><div class='card'>")
    parts.append(f"<p>{_e(band_desc)}</p>")
    parts.append("<p class='note'>Citability Index = (Mention Rate &times; 40) + (Citation Rate &times; 60). "
                  "Citation is weighted higher than mention because being cited as a source means the page "
                  "itself is doing the work, not just brand-name recognition.</p></div>")

    parts.append("<h2>Methodology Note</h2>")
    parts.append(f"<div class='disclaimer'>{_e(METHODOLOGY_DISCLAIMER)}</div>")

    parts.append("<footer>Small Factory 5 — Built to be cited.</footer>")
    parts.append("</div></body></html>")
    return "\n".join(parts)


def generate_html(client_slug):
    return _render_html(_gather(client_slug))


def save_html_report(client_slug):
    html_doc = generate_html(client_slug)
    reports_dir = os.path.join(CLIENTS_DIR, client_slug, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    today = datetime.date.today().isoformat()
    path = os.path.join(reports_dir, f"{today}-{client_slug}-ai-visibility-report.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html_doc)
    return path
