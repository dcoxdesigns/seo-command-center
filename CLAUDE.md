# Small Factory 5 — SEO/GEO Practice Instructions

## What this is
Small Factory 5 is a solo GEO/AI-visibility practice. Positioning: "Built to be cited."
We help brands (any industry — no vertical exclusivity) get found and cited by AI search
engines (ChatGPT, Perplexity, Gemini, Copilot, Google AI Mode, Google AI Overviews).

## The Framework (applies to every client, every page)
Every page gets evaluated against the same five levers:
1. **Citability** — is there a clean, quotable, fact-checkable claim an AI would lift?
2. **Conversational Alignment** — does the content match how people actually ask AI questions?
3. **Authority Signals** — credentials, sourcing, author/entity signals, E-E-A-T markers.
4. **Factual Density** — specific numbers, names, dates vs. vague marketing language.
5. **Structured Clarity** — headings, schema, answer-first structure, scannability.

Full detail lives in `config/five-lever-framework.md`. Don't restate the framework in every
output — reference it, apply it, and only explain a lever if the client-facing report needs it.

## Client structure
Each client gets a subfolder under `clients/<client-name>/`:
- `client-facts.md` — company facts, competitors, brand voice notes, correction log
  (same purpose as Ellison's fact-correction pattern — prevents drift/hallucination across sessions)
- `data/` — exports, crawl data, keyword data
- `reports/` — delivered work product

Start every new client from `clients/_template/`.

## Working rules
- **No vertical assumptions.** Don't default to B2B/industrial framing just because that's
  the operator's day-job background. Read `client-facts.md` fresh for tone and audience.
- **Ask before assuming client identity.** If a request doesn't specify which client, ask —
  never guess and apply the wrong company's facts to a report.
- **Never write directly to a live site.** Draft only. All schema/code changes are handed
  off as dev-ready tickets, not implemented directly.
- **Cite sources for any competitive or market claim** in client reports — no invented stats.
- **Keep this repo fully separate from any employer work.** No employer-specific data,
  credentials, or internal facts belong in this repo, ever.

## Output conventions
- Client-facing reports: same pass/fix scorecard + prioritized fix list format as the
  seo-geo-page-reviewer workflow (self-serve fixes vs. dev/IT fixes, split clearly).
- Internal notes / drafts: Markdown, saved to the relevant client's `reports/` folder.
- Anything meant to leave the repo as a deliverable: flag it and ask if it should be
  formatted as a Word doc or PDF before finalizing.

## Permission boundaries
- OK without asking: reading data files, drafting reports, running analysis, searching web
  for competitive/source context.
- Ask first: sending anything to a client, publishing/exporting a final deliverable,
  deleting any client folder or file.
