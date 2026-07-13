# Workflow: Full-Site Crawl & Technical Baseline (Step 1)

Run this at the start of every engagement, before touching content. It turns a crawler
export into the technical baseline that step 3 (linking map) and every later phase gets
measured against.

## Before starting
1. Confirm which client this is for. If not stated, ask — do not guess.
2. Read `clients/<client>/client-facts.md`.
3. Check `clients/<client>/data/crawl/` (or the legacy `data/crawl/`) for a crawl export.
   If nothing's there, say so and ask for one — don't proceed on an assumed site structure.

## Getting the crawl export
This repo doesn't fetch crawl data itself — a licensed crawler does the crawling, this
workflow reads its export. Screaming Frog is the default: run a full crawl of the client's
domain, then export and drop these reports into `clients/<client>/data/crawl/`:

- **Internal All** (`internal_all.csv`) — every internal URL: status code, indexability,
  title, meta description, H1, word count, canonical. This is the core baseline input.
- **All Inlinks** (`all_inlinks.csv`) — every internal link, source → destination. Needed
  here for orphan detection and again in step 3 for the linking map.

No Screaming Frog license yet? A partial baseline can be built from `Internal All` alone —
say so in the report and flag the linking analysis as pending step 3.

## Steps
1. **Load the crawl export(s).** Use the real column names from the file — don't assume a
   schema. If a report is missing a column this workflow expects, note it and work with
   what's there.
2. **Indexation summary.** Count pages by `Indexability` (Indexable / Non-Indexable, with
   the non-indexable reason: 404, canonicalised, noindex, redirect, etc.). Lead with the
   total page count and what fraction is actually indexable.
3. **Status code issues.** List every non-200 URL (4xx, 5xx, 3xx) — these are the errors to
   fix first, they block everything downstream.
4. **Duplicate content.** Group by `Title 1`, `Meta Description 1`, and `H1-1` — flag any
   value shared across more than one URL as a duplicate to resolve (rewrite or
   canonicalize).
5. **Thin content.** Flag indexable pages below a reasonable word-count floor (use ~300
   words as the default threshold unless `client-facts.md` says otherwise for this
   client's content type). Thin pages are candidates for the five-lever review (step 5) or
   consolidation.
6. **Orphan check (if `all_inlinks.csv` is present).** Cross-reference `Internal All`
   against `All Inlinks` — any indexable URL that never appears as a `Destination` has zero
   internal inlinks. Flag these; full linking remediation is step 3's job, but surface the
   list here since it's a direct baseline finding.
7. **Missing on-page basics.** Flag indexable pages missing a title, meta description, or
   H1 outright — distinct from duplicates, these have nothing at all.

## Output
A technical baseline report: page counts, indexation breakdown, prioritized error list,
duplicate/thin/orphan/missing-element flags. Saved to
`clients/<client>/reports/YYYY-MM-DD-technical-baseline.md`.

## Guardrails
- Don't estimate crawl numbers from memory or from the live site "by eye" — read them from
  the export. If no export exists, the baseline doesn't exist yet; say that plainly.
- This step produces findings only. Fixes get scoped later (self-serve vs. dev/IT) once
  step 5 reviews the actual pages.
- Re-run this whole workflow after any major site change (replatform, large content purge,
  migration) — don't treat a six-month-old crawl as current.
