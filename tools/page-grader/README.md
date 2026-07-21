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
  heuristic gets this right. It also establishes the target query/persona/
  funnel-stage and scores a separate SEO Intent Match table (intent match,
  subtopic coverage, answer extractability, title/meta/H1-vs-query
  alignment, technical/schema health) alongside the five GEO levers.
- **Internal linking** (`grader/crawl.py`) — deterministic, not AI-judged:
  reads a Screaming Frog export (`clients/<slug>/data/crawl/internal_all.csv`
  + `all_inlinks.csv`) if one exists for the client, and finds real inbound
  candidates (topical overlap with other crawled pages, labeled "confirmed
  gap" only when inlink data is available to actually check) and outbound
  opportunities (anchor text that already appears verbatim in the page's own
  copy — never invented). Silently skipped if no crawl export exists.
- **Scoring** (`grader/scoring.py`) — every SEO-intent item and GEO lever is
  scored 0-10 by the AI (the source of truth), with a Pass/Needs Work/Fail
  label derived from it rather than chosen separately. Each scorecard's five
  items average into a composite **SEO Intent Score** and **GEO Score**,
  0-100 each, reported side by side and never blended into one number.
- **Re-grade** (`grader/regrade.py`) — if this exact URL was reviewed before
  for this client, a fresh review automatically becomes a re-grade: real
  score deltas (old → new, both scorecards) plus a per-fix
  shipped/partial/not-shipped status, checked against the live page as it is
  now, not assumed from what was recommended. Matched by exact URL, so this
  only triggers for `--url` runs — `--file`/`--text` have no stable identity
  to diff against.

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
python run.py --url https://example.com/page --run --query "best 5-axis CNC machine for aerospace"
python run.py --file page.html --run --client acme
python run.py --text "paste draft copy here" --run
```

`--query` declares the target query the page should win — if omitted, the
AI infers it from the page instead (and says so if the page doesn't make
its target obvious).

If `--client <slug>` has a crawl export at
`clients/<slug>/data/crawl/internal_all.csv` (a Screaming Frog "Internal
All" report — "All Inlinks" too, if you want confirmed-gap detection
instead of just topical candidates), the report also gets an Internal
Linking section, computed from the real crawl, not guessed. No export?
No section — silently skipped, no error. Free tier of Screaming Frog
covers sites under 500 URLs; a license is needed above that.

Re-running `--url` for the same client+page automatically re-grades against
the last review of that exact URL — no flag needed, it just finds the prior
`clients/<slug>/reports/*.json` sidecar and diffs against it.

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

- **Live-verified 2026-07-20** — a full run against a real page returned a
  well-formed, accurate five-lever scorecard (see `ai_judge.py`'s module
  docstring for what it found). `MAX_TOKENS` was bumped from 4000 to 8000
  after the first live run truncated mid-JSON on a full report.
- **Guardrails are prompt-level, not code-enforced.** The AI is instructed
  not to invent facts/specs/competitor claims, same as the manual workflow's
  guardrails — but that's an instruction to the model, not something this
  tool can mechanically verify. Spot-check rewrites before they ship, same
  as you would for a manually-written review.
- **No CLI-native web UI**, but a client-facing version now exists —
  see `smallfactory5-site`'s `/tools/page-review/` (password-protected,
  TypeScript port of this same logic since the two repos can't share code
  directly). This Python CLI tool remains the internal/unrestricted version.
