# Workflow: Page Review (SEO + GEO)

This is the core deliverable workflow — run this whenever the request is "review this page,"
"audit this URL," "score this page," or similar, for any client.

## Before starting
1. Confirm which client this is for. If not stated, ask — do not guess.
2. Read `clients/<client>/client-facts.md` in full before touching the page.
3. Read `config/five-lever-framework.md` and `config/brand-voice.md`.

## Steps
1. **Pull the page content.** If given a URL, fetch it. If given a file/paste, use that
   directly.
2. **Score against all five levers** from `config/five-lever-framework.md`:
   Citability, Conversational Alignment, Authority Signals, Factual Density,
   Structured Clarity. Each gets: Pass / Needs Work / Fail, with a one-line reason.
3. **Check against client-facts.md** — flag anything on the page that contradicts a known
   fact, an off-limits claim, or the client's brand voice guidance.
4. **Write prioritized fixes**, split into two lists:
   - **Self-serve** — copy/content changes the client (or you) can make directly.
   - **Dev/IT required** — schema markup, technical structure, anything needing a developer.
5. **Draft the rewritten elements** where relevant: title tag, meta description, H1,
   answer-first opening paragraph, FAQ block if applicable.
6. **If schema is needed**, write it as a copy-ready JSON-LD snippet plus a short dev ticket
   description (what it's for, where it goes).
7. **Fill the report template** (`reports/templates/page-review-template.md`) with all of
   the above, in Small Factory 5's brand voice.
8. **Save the output** to `clients/<client>/reports/` with a dated filename, e.g.
   `2026-07-05-page-review-homepage.md`.

## Guardrails
- Never invent a competitor claim, statistic, or fact not present in `client-facts.md` or
  found via an actual search/fetch.
- Never write directly to a live site — this workflow produces a draft/report only.
- If the page content can't be retrieved, say so — don't fabricate a review of a page you
  didn't actually read.
