"""Calls Claude to score the judgment-based levers (Citability, Conversational
Alignment, Authority Signals, Factual Density) and draft fixes/rewrites —
automating what prompts/page-reviewer.md normally does in a live Claude Code
session. Structural facts (heading hierarchy, schema presence) are computed
by structural.py and passed in as ground truth, not re-guessed here.

Live-verified 2026-07-20 against the real Anthropic API (via the TypeScript
port in smallfactory5-site's /tools/page-review/, same prompt/schema logic) —
a full run against smallfactory5.com's homepage returned a well-formed,
accurate five-lever scorecard with a genuinely non-obvious finding (the page
says "I" throughout but never states a name in visible text). MAX_TOKENS was
bumped from 4000 to 8000 after the first live run truncated mid-JSON on a
full report — that fix is applied here too.
"""

import json
import os
import urllib.error
import urllib.request

from . import config_docs

URL = "https://api.anthropic.com/v1/messages"
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")
MAX_TOKENS = 8000

RESPONSE_SCHEMA_NOTE = """
Respond with ONLY valid JSON, no markdown fences, no commentary before or
after, matching exactly this shape:

{
  "target": {
    "query": "the real query/queries this page should win — if a declared or obvious keyword isn't actually a query a person would type or ask, say so here instead of pretending it is",
    "persona": "one sentence: who this page is realistically for, and why — base this on the actual page content and client facts, not a generic guess",
    "funnel_stage": "Awareness|Consideration|Decision"
  },
  "seo_intent": {
    "intent_match": {"score": 0-10, "why": "does the page answer the actual question behind the query, not just contain the keyword?"},
    "subtopic_coverage": {"score": 0-10, "why": "are the must-cover subtopics for this query actually present?"},
    "answer_extractability": {"score": 0-10, "why": "can a reader get the answer above the fold, without scrolling past a hero or company history?"},
    "title_meta_h1_alignment": {"score": 0-10, "why": "do title, meta, and H1 all match the QUERY (not just each other)?"},
    "technical_schema_health": {"score": 0-10, "why": "ground this in the structural facts already given (schema_types_found, jsonld_parse_errors) — don't re-guess what's already verified"}
  },
  "summary": "2-3 sentences: overall state, the single biggest opportunity, the single biggest risk if nothing changes",
  "levers": {
    "citability": {"score": 0-10, "why": "one line"},
    "conversational_alignment": {"score": 0-10, "why": "one line"},
    "authority_signals": {"score": 0-10, "why": "one line"},
    "factual_density": {"score": 0-10, "why": "one line"},
    "structured_clarity": {"score": 0-10, "why": "one line"}
  },
  "fixes_self_serve": ["fix 1", "fix 2"],
  "fixes_dev": ["fix 1"],
  "rewritten": {
    "title_tag": {"current": "...", "suggested": "..."},
    "meta_description": {"current": "...", "suggested": "..."},
    "h1": {"current": "...", "suggested": "..."},
    "answer_first_opening": "...",
    "faq": [{"q": "...", "a": "..."}]
  },
  "schema_needed": true,
  "schema_json_ld": {},
  "schema_dev_note": "where this goes, what it's for",
  "prioritize_first": "1-2 sentences"
}

Every "score" field is an integer 0-10, not a bucket label — this is the
source of truth a Pass/Needs Work/Fail label and a composite /100 score both
get derived from later, so calibrate it for real, don't just pick 7 for
everything to be safe:
- 9-10: exceptional, nothing meaningful left to improve.
- 7-8: solid, clears the bar (this is what "Pass" means).
- 4-6: workable but has real, specific gaps ("Needs Work").
- 1-3: fails to do the job ("Fail").
- 0: not attempted / entirely absent.
Use the full range. A page doesn't need to cluster at 6-8 to be a valid
review — if something is genuinely a 9 or genuinely a 2, say so.

Use null for "suggested" in two cases: (1) the current page doesn't give you
enough to write a real rewrite — do not invent one, or (2) the current
version is already strong and doesn't need a rewrite. Never repeat the
current text verbatim as the "suggested" value — that reads as a bug to
whoever's looking at the report, not a genuine "no change needed" signal.
Set "schema_needed" to false and leave schema_json_ld as {} if no new schema
is warranted.
"""

GUARDRAILS = """
Guardrails, same as this repo's page-reviewer.md workflow:
- Never invent a competitor claim, statistic, spec, or fact that isn't in the
  page content or the client facts below. If a rewrite would need a real
  number you don't have (price, weight, dimension, date), say so in the
  "why" or leave the field null instead of inventing one.
- Score honestly across the full 0-10 range — a page doesn't need low scores
  everywhere to be a valid review, and it doesn't need to cluster in the
  middle to seem fair.
- Target query, persona, and funnel stage are inferred from the actual page
  content (and client facts, if given) — not a generic guess. If the page
  genuinely doesn't make its target audience or query clear, say that
  plainly in "why" fields rather than inventing a confident-sounding answer.
- This produces a draft report only. Nothing here gets written to a live site.
"""


def build_prompt(page_text, structural_facts, client_slug=None, target_query=None):
    parts = [
        "You are running Small Factory 5's page review workflow — both the SEO intent-match "
        "scorecard and the five-lever GEO framework — exactly as a human reviewer would.",
        "",
        "## Five-Lever Framework (the GEO scoring standard)",
        config_docs.five_lever_framework(),
        "",
        "## Brand Voice (write every 'why', fix, and rewrite in this voice)",
        config_docs.brand_voice(),
    ]

    facts = config_docs.client_facts(client_slug)
    if facts:
        parts += ["", "## Client Facts (check the page against this; flag contradictions)", facts]

    if target_query:
        parts += [
            "",
            "## Declared target query (from the operator)",
            f'"{target_query}"',
            "Score seo_intent against this declared query. If it genuinely isn't a real query pattern "
            "a person would type or ask, say so in intent_match's \"why\" instead of scoring against it "
            "as if it were valid.",
        ]
    else:
        parts += [
            "",
            "## Target query",
            "No target query was declared — infer the real query/queries this page is actually trying "
            "to win from the page content itself, and score seo_intent against that inferred query.",
        ]

    parts += [
        "",
        "## Structural facts already verified by direct HTML parsing (ground truth — don't re-guess these)",
        json.dumps({
            "title": structural_facts.get("title"),
            "title_length": structural_facts.get("title_length"),
            "meta_description": structural_facts.get("meta_description"),
            "h1_count": structural_facts.get("h1_count"),
            "heading_jumps": structural_facts.get("heading_jumps"),
            "headings": structural_facts.get("headings"),
            "schema_types_found": structural_facts.get("schema_types"),
            "jsonld_parse_errors": structural_facts.get("jsonld_parse_errors"),
            "total_images": structural_facts.get("total_images"),
            "images_missing_alt": structural_facts.get("images_missing_alt"),
            "word_count": structural_facts.get("word_count"),
        }, indent=2),
        "",
        "## Page content",
        page_text[:12000],
        "",
        GUARDRAILS,
        RESPONSE_SCHEMA_NOTE,
    ]
    return "\n".join(parts)


def score_page(page_text, structural_facts, client_slug=None, api_key=None, target_query=None):
    api_key = api_key or os.environ["ANTHROPIC_API_KEY"]
    prompt = build_prompt(page_text, structural_facts, client_slug, target_query)

    body = {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    req = urllib.request.Request(URL, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} from Claude API: {e.read().decode('utf-8', errors='replace')[:300]}") from e

    text = "".join(block.get("text", "") for block in raw.get("content", []) if block.get("type") == "text")
    try:
        return json.loads(text), raw
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Claude didn't return valid JSON: {e}\nRaw text: {text[:500]}") from e
