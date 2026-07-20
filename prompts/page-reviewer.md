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
2. **Establish the target.** State the real query/queries this page should win (flag if a
   declared or obvious keyword isn't actually a query a person would type or ask), the
   realistic persona this page is for, and the funnel stage (Awareness / Consideration /
   Decision). Infer these from the page content and client-facts.md — don't guess generically.
3. **Score SEO intent match**: Intent Match, Subtopic Coverage, Answer Extractability,
   Title/Meta/H1 Alignment (against the query, not just each other), Technical/Schema
   Health. Each gets a 0-10 score (9-10 exceptional, 7-8 Pass, 4-6 Needs Work, 1-3 Fail,
   0 absent — use the full range, don't cluster at 6-8 to seem fair) with a one-line
   reason. Average the five scores and scale to 100 for the section's composite
   **SEO Intent Score**.
4. **Score against all five GEO levers** from `config/five-lever-framework.md`:
   Citability, Conversational Alignment, Authority Signals, Factual Density,
   Structured Clarity. Same 0-10 scale as step 3, same composite math, giving the
   **GEO Score**. Report both scores side by side — never blend them into one number.
5. **Check against client-facts.md** — flag anything on the page that contradicts a known
   fact, an off-limits claim, or the client's brand voice guidance.
6. **Write prioritized fixes**, split into two lists:
   - **Self-serve** — copy/content changes the client (or you) can make directly.
   - **Dev/IT required** — schema markup, technical structure, anything needing a developer.
7. **Draft the rewritten elements** where relevant: title tag, meta description, H1,
   answer-first opening paragraph, FAQ block if applicable.
8. **If schema is needed**, write it as a copy-ready JSON-LD snippet plus a short dev ticket
   description (what it's for, where it goes).
9. **Fill the report template** (`reports/page-review-template.md`) with all of
   the above, in Small Factory 5's brand voice.
10. **Save the output** to `clients/<client>/reports/` with a dated filename, e.g.
   `2026-07-05-page-review-homepage.md`.

## Guardrails
- Never invent a competitor claim, statistic, or fact not present in `client-facts.md` or
  found via an actual search/fetch.
- Never write directly to a live site — this workflow produces a draft/report only.
- If the page content can't be retrieved, say so — don't fabricate a review of a page you
  didn't actually read.
