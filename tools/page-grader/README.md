# SF5 Page Grader

Automates the five-lever page review (`prompts/page-reviewer.md`) that
normally runs as a live Claude Code session. No third-party dependencies —
standard library only, same convention as `fetchers/` and the other `tools/`.

Deliberately **not** a clone of a generic technical-SEO grader (title length,
viewport, HTTPS). It scores the same five levers Small Factory 5 actually
sells: Citability, Conversational Alignment, Authority Signals, Factual
Density, Structured Clarity.

## How it splits the work

- **Structural checks** (`grader/structural.py`) — plain HTML parsing, no API
  call, no cost: heading hierarchy and skips, JSON-LD presence/validity and
  schema types, image alt coverage, title/meta length. This is ground truth
  fed into the AI prompt, not re-guessed by it.
- **Judgment checks** (`grader/ai_judge.py`) — Claude scores Citability,
  Conversational Alignment, Authority Signals, and Factual Density, and
  drafts the fixes and rewritten elements. These require actually reading
  and understanding the content, not just parsing tags — no rule-based
  heuristic gets this right.

The prompt is built from `config/five-lever-framework.md` and
`config/brand-voice.md` **read at runtime**, not copied into this tool's
code — if those docs change, this tool's scoring criteria and voice change
with them automatically.

## Setup

```bash
cd tools/page-grader
cp .env.example .env
# fill in a real ANTHROPIC_API_KEY
```

## Running it

```bash
python run.py --url https://example.com/page                       # dry run, no API call
python run.py --url https://example.com/page --run                  # real run, prints report (no client given)
python run.py --url https://example.com/page --run --client acme    # saves to clients/acme/reports/
python run.py --file page.html --run --client acme
python run.py --text "paste draft copy here" --run
```

Always dry-runs by default — same safety pattern as every other tool in this
repo that spends real API money. One review is one Claude API call, roughly
$0.05-$0.20 depending on page length (check console.anthropic.com for
actuals).

Giving `--client <slug>` does two things: it reads
`clients/<slug>/client-facts.md` (if present) so the review can flag
off-limits claims and brand-voice contradictions, matching step 3 of
`prompts/page-reviewer.md`, and it saves the report to
`clients/<slug>/reports/`. Without `--client`, the report just prints —
there's no client-facts.md to check against and nowhere sensible to save it.

## Output

A markdown file in the exact shape of `reports/page-review-template.md` —
scorecard, self-serve/dev fixes, rewritten title/meta/H1/FAQ, a schema
snippet if one's warranted, and a "what I'd prioritize first" line. Feed it
straight into `tools/report-to-html/render.py` for a client-facing HTML copy.

Every generated report ends with a line disclosing it's an automated first
pass — this doesn't pretend to replace a human spot-check before something
ships to a client, and it says so on the report itself.

## Known gaps

- **Not live-tested against a real Anthropic key** while building this — the
  API call shape follows Anthropic's documented Messages API, but hasn't hit
  a real endpoint yet. Verify against
  https://docs.anthropic.com/en/api/messages before trusting a real run.
- **Guardrails are prompt-level, not code-enforced.** The AI is instructed
  not to invent facts/specs/competitor claims, same as the manual workflow's
  guardrails — but that's an instruction to the model, not something this
  tool can mechanically verify. Spot-check rewrites before they ship, same
  as you would for a manually-written review.
- **No web UI.** CLI only, matching the rest of `tools/`. Whether this
  becomes a client-facing self-serve tool on the site is a separate decision
  from building the underlying engine.
