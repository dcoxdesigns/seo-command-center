"""Generates printable/emailable reports for one client's latest run —
Markdown (house style matches reports/page-review-template.md) and a
self-contained HTML version (single file, opens in any browser and
prints/exports to PDF cleanly — the more reliable format for actually
emailing to a client, since plain .md doesn't render images or tables in
most mail clients).

The HTML deliberately matches smallfactory5-site's actual design system —
same CSS tokens, same Google Fonts, same inline SVG logo used by the
Page Review Tool's report (src/lib/grader/renderReport.ts /
GraderReportStyles.astro on that repo) — rather than a one-off look, so
every SF5 client deliverable is visually the same product.
"""

import datetime
import html as html_lib
import os

from . import citability, competitors, db
from .config import CLIENTS_DIR, load_client_config
from .platforms import ALL as ALL_PLATFORMS
from .runner import REPLICATES_PER_PROMPT

PLATFORM_NAMES = [p.NAME for p in ALL_PLATFORMS]
PLATFORM_LABELS = {"chatgpt": "ChatGPT", "perplexity": "Perplexity", "gemini": "Gemini"}

# Same mark used at the top of every Page Review Tool report on
# smallfactory5-site — kept identical (not regenerated) so both deliverable
# types show the exact same logo.
LOGO_SVG = (
    '<svg viewBox="0 0 4000 3000" xmlns="http://www.w3.org/2000/svg" '
    'style="fill-rule:evenodd;clip-rule:evenodd;stroke-linejoin:round;stroke-miterlimit:2;">'
    '<path fill="#15171B" d="M1894,2704l-1132.394,0l-0,-754.146l375.79,-366.812l0,305.249l398.876,-342.444l0,310.38l'
    '357.727,-311.897l0,-524.33l403.47,0l65.53,-634l162,0l77.817,634l44.654,0l65.53,-634l162,0l77.817,634l64.654,0l'
    '65.53,-634l162,0l77.817,634l256.183,0l0,1685l-1685,0l0,-1Z"/>'
    '<text x="2206px" y="2475px" style="font-family:\'Arial-Black\',\'Arial Black\',sans-serif;font-weight:900;'
    'font-size:1592.889px;fill:#EDECE4;">5</text>'
    '<g transform="matrix(1.435334,0,0,1.435334,687.660465,666.494491)">'
    '<text x="210px" y="1094px" style="font-family:\'Impact\',sans-serif;font-stretch:condensed;font-size:184.278px;'
    'fill:#EDECE4;">SMALL</text>'
    '<text x="210px" y="1260.667px" style="font-family:\'Impact\',sans-serif;font-stretch:condensed;'
    'font-size:184.278px;fill:#EDECE4;">F<tspan x="279.644px 373.223px " y="1260.667px 1260.667px ">AC</tspan>'
    'TORY</text></g></svg>'
)

# Matches the score-row coloring convention from GraderReportStyles.astro
# (pass/needs-work/fail), extended to a fourth "strong" tier since bands
# here aren't binary pass/fail.
BAND_CLASS = {
    "Low visibility": "band-fail",
    "Emerging": "band-needswork",
    "Solid": "band-pass",
    "Strong": "band-strong",
}

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
:root{
  --paper:#EDECE4;
  --paper-dark:#E1DFD5;
  --ink:#15171B;
  --steel:#5B6472;
  --blueprint:#2C4870;
  --signal:#F2A900;
  --line:#C9C6BA;
  --radius:2px;
}
*{box-sizing:border-box;}
body{margin:0;background:var(--paper);color:var(--ink);font-family:'IBM Plex Sans',sans-serif;line-height:1.5;-webkit-font-smoothing:antialiased;}
.wrap{max-width:820px;margin:0 auto;padding:48px 32px 64px;}
.report-header{display:flex;flex-direction:column;align-items:center;text-align:center;gap:10px;padding-bottom:24px;margin-bottom:8px;border-bottom:2px solid var(--blueprint);}
.report-header svg{width:72px;height:54px;}
.report-header .tagline{font-family:'Big Shoulders Display',sans-serif;font-weight:800;text-transform:uppercase;letter-spacing:0.02em;font-size:1.9rem;line-height:1;color:var(--ink);}
.report-header h1{font-family:'IBM Plex Sans',sans-serif;font-weight:600;text-transform:none;letter-spacing:0;font-size:1.15rem;color:var(--steel);margin:0;}
.meta{font-family:'IBM Plex Mono',monospace;font-size:0.72rem;letter-spacing:0.08em;text-transform:uppercase;color:var(--steel);text-align:center;margin:8px 0 0;}
h2{font-size:1.2rem;font-weight:700;color:var(--blueprint);border-bottom:2px solid var(--blueprint);padding-bottom:6px;margin:44px 0 14px;}
.card{background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:24px 28px;margin-bottom:8px;}
.band-chip{display:inline-flex;align-items:center;gap:14px;padding:10px 18px;border-radius:var(--radius);}
.score{font-size:2.6rem;font-weight:800;font-family:'Big Shoulders Display',sans-serif;}
.band{font-size:1.05rem;font-weight:600;font-family:'IBM Plex Mono',monospace;text-transform:uppercase;letter-spacing:0.04em;}
.band-pass{background:#E3F2E5;} .band-pass .score,.band-pass .band{color:#1E5C2E;}
.band-needswork{background:#FDF3DC;} .band-needswork .score,.band-needswork .band{color:#8A5A00;}
.band-fail{background:#FBEAE8;} .band-fail .score,.band-fail .band{color:#A62D20;}
.band-strong{background:#E4EAF2;} .band-strong .score,.band-strong .band{color:var(--blueprint);}
table{width:100%;border-collapse:collapse;margin:12px 0;background:#fff;}
th,td{text-align:left;padding:9px 12px;border:1px solid var(--line);font-size:0.92rem;}
th{background:var(--blueprint);color:var(--paper);font-family:'IBM Plex Mono',monospace;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.04em;}
.note{color:var(--steel);font-size:0.88rem;font-style:italic;}
.trend-flagged{color:#A62D20;font-weight:700;}
.cell-cited{color:#1E5C2E;font-weight:700;}
.cell-mentioned{color:#8A5A00;}
.cell-none{color:var(--steel);}
.cell-skipped{color:var(--steel);font-style:italic;}
.disclaimer{background:#fff;border:1px solid var(--line);border-left:4px solid var(--signal);border-radius:var(--radius);padding:14px 20px;font-size:0.86rem;color:var(--steel);margin-top:8px;}
footer{text-align:center;color:var(--steel);font-size:0.68rem;font-style:italic;font-family:'IBM Plex Mono',monospace;margin-top:44px;padding-top:14px;border-top:1px solid var(--line);}
"""

_CELL_CLASS = {"cited": "cell-cited", "mentioned": "cell-mentioned", "none": "cell-none", "skipped": "cell-skipped"}


def _e(text):
    return html_lib.escape(str(text))


def _render_html(data):
    cfg = data["cfg"]
    matrix = data["matrix"]
    blended = data["blended"]
    band = data["band"]
    band_desc = data["band_desc"]
    band_class = BAND_CLASS.get(band, "band-fail")

    parts = []
    parts.append("<!doctype html><html lang='en'><head><meta charset='utf-8'>")
    parts.append(f"<title>AI Visibility Report — {_e(cfg.client)}</title>")
    parts.append(
        "<link rel='preconnect' href='https://fonts.googleapis.com'>"
        "<link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>"
        "<link href='https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@600;800;900"
        "&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap' rel='stylesheet'>"
    )
    parts.append(f"<style>{_HTML_STYLE}</style></head><body><div class='wrap'>")

    parts.append(f"<div class='report-header'>{LOGO_SVG}"
                  f"<div class='tagline'>Built to be cited.</div>"
                  f"<h1>AI Visibility Report — {_e(cfg.client)}</h1></div>")
    parts.append(f"<div class='meta'>Date: {_e(data['today'])} &nbsp;·&nbsp; Prepared by: Small Factory 5</div>")

    parts.append("<h2>Summary</h2><div class='card'>")
    parts.append(f"<div class='band-chip {band_class}'>"
                  f"<span class='score'>{blended['citability_index']}</span>"
                  f"<span class='band'>{_e(band)}</span></div>")
    parts.append(f"<p style='margin-top:16px;'>{_e(cfg.client)}'s blended Citability Index is "
                  f"<strong>{blended['citability_index']} ({_e(band)})</strong> across {len(matrix)} tracked "
                  f"prompt(s) on {_e(', '.join(PLATFORM_LABELS[p] for p in PLATFORM_NAMES))}."
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

    parts.append(f"<footer>Report generated by David Cox, Small Factory 5 — {_e(data['today'])}</footer>")
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
