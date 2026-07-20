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
  "summary": "2-3 sentences: overall state, the single biggest opportunity, the single biggest risk if nothing changes",
  "levers": {
    "citability": {"score": "Pass|Needs Work|Fail", "why": "one line"},
    "conversational_alignment": {"score": "Pass|Needs Work|Fail", "why": "one line"},
    "authority_signals": {"score": "Pass|Needs Work|Fail", "why": "one line"},
    "factual_density": {"score": "Pass|Needs Work|Fail", "why": "one line"},
    "structured_clarity": {"score": "Pass|Needs Work|Fail", "why": "one line"}
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

Use null (not a guess) for any rewritten-element field where the current page
doesn't give you enough to write a real suggestion. Set "schema_needed" to
false and leave schema_json_ld as {} if no new schema is warranted.
"""

GUARDRAILS = """
Guardrails, same as this repo's page-reviewer.md workflow:
- Never invent a competitor claim, statistic, spec, or fact that isn't in the
  page content or the client facts below. If a rewrite would need a real
  number you don't have (price, weight, dimension, date), say so in the
  "why" or leave the field null instead of inventing one.
- Score honestly. A page doesn't need five failures to be a valid review —
  if something genuinely passes, say Pass.
- This produces a draft report only. Nothing here gets written to a live site.
"""


def build_prompt(page_text, structural_facts, client_slug=None):
    parts = [
        "You are running Small Factory 5's five-lever page review workflow. "
        "Score this page against the framework below exactly as a human reviewer would.",
        "",
        "## Five-Lever Framework (the scoring standard)",
        config_docs.five_lever_framework(),
        "",
        "## Brand Voice (write every 'why', fix, and rewrite in this voice)",
        config_docs.brand_voice(),
    ]

    facts = config_docs.client_facts(client_slug)
    if facts:
        parts += ["", "## Client Facts (check the page against this; flag contradictions)", facts]

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


def score_page(page_text, structural_facts, client_slug=None, api_key=None):
    api_key = api_key or os.environ["ANTHROPIC_API_KEY"]
    prompt = build_prompt(page_text, structural_facts, client_slug)

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
