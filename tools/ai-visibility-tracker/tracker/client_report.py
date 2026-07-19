"""Generates a printable/emailable Markdown report for one client's latest
run — same house style as reports/page-review-template.md (header line,
horizontal rules, tables, a plain-English summary up top).
"""

import datetime
import os

from . import citability, competitors, db
from .config import CLIENTS_DIR, load_client_config
from .platforms import ALL as ALL_PLATFORMS

PLATFORM_NAMES = [p.NAME for p in ALL_PLATFORMS]
PLATFORM_LABELS = {"chatgpt": "ChatGPT", "perplexity": "Perplexity", "gemini": "Gemini"}


def _cell(row):
    if row is None:
        return "not tested"
    if row["cited"]:
        return "**Cited**"
    if row["mentioned"]:
        return "Mentioned"
    return "—"


def generate_markdown(client_slug):
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
    conn.close()

    today = datetime.date.today().isoformat()
    blended = latest["blended"]
    band = latest["band"]
    band_desc = citability.BAND_DESCRIPTIONS.get(band, "")

    lines = []
    lines.append(f"# AI Visibility Report — {cfg.client}")
    lines.append(f"**Client:** {cfg.client} | **Date:** {today} | **Prepared by:** Small Factory 5")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Summary")
    trend_sentence = ""
    if previous is not None:
        direction = "up" if delta > 0 else ("down" if delta < 0 else "unchanged")
        trend_sentence = f" That's {direction} {abs(delta):.1f} points since the previous run on {previous['timestamp'][:10]}."
        if flagged:
            trend_sentence += " This drop is significant enough to flag directly."
    lines.append(
        f"{cfg.client}'s blended Citability Index is **{blended['citability_index']} ({band})** "
        f"across {len(matrix)} tracked prompt(s) on {', '.join(PLATFORM_LABELS[p] for p in PLATFORM_NAMES)}."
        f"{trend_sentence} {band_desc}"
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Citability Index")
    lines.append("")
    lines.append(f"**Blended: {blended['citability_index']} ({band})**")
    lines.append("")
    lines.append("| Platform | Citability Index | Mention Rate | Citation Rate | Prompts Tested |")
    lines.append("|---|---|---|---|---|")
    for platform in PLATFORM_NAMES:
        idx = latest["per_platform"][platform]
        label = PLATFORM_LABELS[platform]
        if idx["n"] == 0:
            lines.append(f"| {label} | — | — | — | not tested (no API key set) |")
        else:
            lines.append(
                f"| {label} | {idx['citability_index']} | {idx['mention_rate']*100:.0f}% "
                f"| {idx['citation_rate']*100:.0f}% | {idx['n']} |"
            )
    lines.append("")
    if previous is not None:
        arrow = "up" if delta > 0 else ("down" if delta < 0 else "flat")
        flag_note = " — **flagged**" if flagged else ""
        lines.append(f"**Trend:** {arrow} {delta:+.1f} vs. previous run ({previous['timestamp'][:10]}){flag_note}")
    else:
        lines.append("**Trend:** first tracked run — no prior data yet.")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Who's Getting Cited Instead")
    if top_domains:
        lines.append(f"*(Other domains appearing as sources across {cfg.client}'s tracked prompts this run.)*")
        lines.append("")
        lines.append("| Domain | Times Cited | Example Prompt |")
        lines.append("|---|---|---|")
        for d in top_domains:
            lines.append(f"| {d['domain']} | {d['count']} | “{d['example_prompt']}” |")
    else:
        lines.append(f"No competing domains were cited across {cfg.client}'s tracked prompts this run.")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Prompts Tracked")
    lines.append("")
    header = "| Prompt | " + " | ".join(PLATFORM_LABELS[p] for p in PLATFORM_NAMES) + " |"
    sep = "|---|" + "|".join(["---"] * len(PLATFORM_NAMES)) + "|"
    lines.append(header)
    lines.append(sep)
    for prompt, by_platform in matrix.items():
        cells = " | ".join(_cell(by_platform.get(p)) for p in PLATFORM_NAMES)
        lines.append(f"| {prompt} | {cells} |")
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

    return "\n".join(lines)


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
