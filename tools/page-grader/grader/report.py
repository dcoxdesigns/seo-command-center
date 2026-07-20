"""Assembles structural facts + the AI judge's output into the exact
reports/page-review-template.md format — so this tool's output is
indistinguishable in shape from a manually-written review, and drops
straight into tools/report-to-html/render.py for a client-facing HTML copy.
"""

import datetime

LEVER_LABELS = {
    "citability": "Citability",
    "conversational_alignment": "Conversational Alignment",
    "authority_signals": "Authority Signals",
    "factual_density": "Factual Density",
    "structured_clarity": "Structured Clarity",
}
LEVER_ORDER = ["citability", "conversational_alignment", "authority_signals", "factual_density", "structured_clarity"]

SEO_INTENT_LABELS = {
    "intent_match": "Intent Match",
    "subtopic_coverage": "Subtopic Coverage",
    "answer_extractability": "Answer Extractability",
    "title_meta_h1_alignment": "Title/Meta/H1 Alignment",
    "technical_schema_health": "Technical/Schema Health",
}
SEO_INTENT_ORDER = [
    "intent_match", "subtopic_coverage", "answer_extractability",
    "title_meta_h1_alignment", "technical_schema_health",
]


def _rewrite_block(label, entry):
    if not entry or (entry.get("current") is None and entry.get("suggested") is None):
        return f"**{label}:**\n- Not enough on the page to draft a rewrite yet."
    current = entry.get("current") or "[not present on the page]"
    suggested = entry.get("suggested") or "[needs real data before this can ship]"
    return f"**{label}:**\n- Current: `{current}`\n- Suggested: `{suggested}`"


def _linking_section(linking):
    lines = ["## Internal Linking", ""]
    inbound = linking.get("inbound") or []
    outbound = linking.get("outbound") or []

    lines.append("**Inbound candidates** *(other pages that could link to this one)*")
    if inbound:
        lines.append("")
        lines.append("| Source Page | Shared Topics | Status |")
        lines.append("|---|---|---|")
        for c in inbound:
            lines.append(f"| [{c['title'] or c['url']}]({c['url']}) | {', '.join(c['shared_terms'])} | {c['status']} |")
    else:
        lines.append("None found — either no topical overlap in the crawl, or this page already has inbound coverage.")
    lines.append("")

    lines.append("**Outbound opportunities** *(anchor text already on this page, pointing at a real destination)*")
    if outbound:
        lines.append("")
        lines.append("| Anchor Text (found on page) | Destination |")
        lines.append("|---|---|")
        for o in outbound:
            lines.append(f"| {o['anchor_text']} | [{o['title'] or o['url']}]({o['url']}) |")
    else:
        lines.append("None found — no other crawled page's title/H1 appears as a real phrase in this page's copy.")
    lines.append("")
    lines.append("*Inbound candidates are topical matches from the crawl, not a confirmed absence of a link, unless "
                  "marked \"confirmed gap\" (only possible when all_inlinks.csv was available). Outbound anchor text "
                  "is never invented — only phrases that genuinely already appear on this page are suggested.*")
    return lines


def build_markdown(*, page_name, client_name, ai_result, structural_facts, linking=None):
    today = datetime.date.today().isoformat()
    lines = []
    lines.append(f"# Page Review — {page_name}")
    lines.append(f"**Client:** {client_name} | **Date:** {today} | **Reviewed by:** Small Factory 5 (automated pass)")
    lines.append("")
    lines.append("---")
    lines.append("")
    target = ai_result.get("target") or {}
    lines.append("## Target")
    lines.append(f"**Query:** {target.get('query', 'N/A')}")
    lines.append(f"**Persona:** {target.get('persona', 'N/A')}")
    lines.append(f"**Funnel Stage:** {target.get('funnel_stage', 'N/A')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Summary")
    lines.append(ai_result.get("summary", "").strip())
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## SEO Intent Match")
    lines.append("")
    lines.append("| Item | Score | Why |")
    lines.append("|---|---|---|")
    for key in SEO_INTENT_ORDER:
        entry = ai_result.get("seo_intent", {}).get(key, {})
        lines.append(f"| {SEO_INTENT_LABELS[key]} | {entry.get('score', 'N/A')} | {entry.get('why', '')} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    if linking is not None:
        lines.extend(_linking_section(linking))
        lines.append("---")
        lines.append("")
    lines.append("## Five-Lever Scorecard (GEO)")
    lines.append("")
    lines.append("| Lever | Score | Why |")
    lines.append("|---|---|---|")
    for key in LEVER_ORDER:
        entry = ai_result.get("levers", {}).get(key, {})
        lines.append(f"| {LEVER_LABELS[key]} | {entry.get('score', 'N/A')} | {entry.get('why', '')} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Fixes — Self-Serve")
    lines.append("*(You or I can make these directly — no developer needed.)*")
    lines.append("")
    fixes_self = ai_result.get("fixes_self_serve") or []
    if fixes_self:
        for i, fix in enumerate(fixes_self, 1):
            lines.append(f"{i}. {fix}")
    else:
        lines.append("None identified this pass.")
    lines.append("")
    lines.append("## Fixes — Dev/IT Required")
    lines.append("*(Needs a developer to implement.)*")
    lines.append("")
    fixes_dev = ai_result.get("fixes_dev") or []
    if fixes_dev:
        for i, fix in enumerate(fixes_dev, 1):
            lines.append(f"{i}. {fix}")
    else:
        lines.append("None identified this pass.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Rewritten Elements")
    lines.append("")
    rewritten = ai_result.get("rewritten") or {}
    lines.append(_rewrite_block("Title tag", rewritten.get("title_tag")))
    lines.append("")
    lines.append(_rewrite_block("Meta description", rewritten.get("meta_description")))
    lines.append("")
    lines.append(_rewrite_block("H1", rewritten.get("h1")))
    lines.append("")
    opening = rewritten.get("answer_first_opening")
    lines.append("**Answer-first opening (if applicable):**")
    lines.append(opening if opening else "Not enough on the page to draft one yet.")
    lines.append("")
    faq = rewritten.get("faq") or []
    lines.append("**FAQ block (if applicable):**")
    if faq:
        for item in faq:
            lines.append(f"- Q: {item.get('q', '')} — A: {item.get('a', '')}")
    else:
        lines.append("None suggested this pass.")
    lines.append("")
    lines.append("---")
    lines.append("")
    if ai_result.get("schema_needed"):
        lines.append("## Schema Recommendation")
        lines.append("```json")
        import json as _json
        lines.append(_json.dumps(ai_result.get("schema_json_ld") or {}, indent=2))
        lines.append("```")
        lines.append(f"**Dev ticket note:** {ai_result.get('schema_dev_note', '')}")
        lines.append("")
        lines.append("---")
        lines.append("")
    lines.append("## What I'd prioritize first")
    lines.append(ai_result.get("prioritize_first", "").strip())
    lines.append("")
    lines.append("---")
    lines.append("*Automated first pass — structural checks (heading hierarchy, schema, images) verified by direct "
                  "HTML parsing; the five levers scored by an AI judge against `config/five-lever-framework.md`. "
                  "Treat this as a draft, same as any first pass — spot-check before it goes to a client.*")
    return "\n".join(lines)
