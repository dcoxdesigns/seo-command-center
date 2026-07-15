# The Nine-Step Workflow

This is Small Factory 5's operating workflow for every client engagement — audit through
ongoing reporting. It's the same nine steps whether the engagement is a single page review
or a full retainer; smaller engagements just stop earlier (a one-off page review is
effectively step 5 with steps 1-2 done informally first).

Five phases, nine steps. Each step below maps the client-facing description to what
actually happens in this repo: which files/prompts/fetchers to use, what gets produced,
where it's saved, and how often it repeats. Where the repo doesn't yet have a built tool
for a step, that's called out — don't imply automation that isn't there.

Every step still runs under the working rules in `AGENTS.md` (read `client-facts.md`
first, cite sources, no invented data) and every report clears the relevant `qa/`
checklist before it ships.

---

## Phase 1 — Audit
*Where every engagement starts. Establishes the baseline everything else is measured against.*

### Step 1A — AI Visibility Grader Snapshot
- **Objective:** A fast, single-input gut-check on the client's current AI visibility before
  the full audit begins — something to anchor the later, more detailed step 2 analysis
  against.
- **Inputs:** The client's domain (`clients/<client>/client-facts.md`).
- **Repo assets:** None — this is a manual step in an external tool, not repo automation.
  Go to [ai.grader.searchinfluence.com](https://ai.grader.searchinfluence.com) and enter the
  client's web address.
- **Output:** Whatever the grader returns (score/grade/summary). Save a screenshot or export
  into `clients/<client>/data/ai-visibility/` so it's available as a reference point when
  step 2 runs.
- **Cadence:** Once, at engagement kickoff — before step 1B.
- **Status:** Manual/external only. No fetcher or in-repo tooling for this step.

### Step 1B — Full-Site Crawl & Technical Baseline
- **Objective:** Map what's actually on the site before touching content — crawlability,
  indexation, page inventory, technical baseline.
- **Inputs:** The client's domain (`clients/<client>/client-facts.md`) and a crawl export.
- **Repo assets:** `prompts/site-crawl-baseline.md`. The crawl itself is still run in an
  external tool — Screaming Frog is the default (a paid license is needed for crawls over
  500 URLs). Export **Internal All** and **All Inlinks** and drop them into
  `clients/<client>/data/crawl/`; sample exports showing the expected columns are in
  `data/crawl/`.
- **Output:** A technical baseline report — page count, indexation status, crawl errors,
  duplicate/thin/orphan content flags — saved to `clients/<client>/reports/`.
- **Cadence:** Once, at engagement start. Re-run if the site has a major structural change
  (replatform, large content purge, migration).
- **Status:** Built (import-based — no in-repo fetcher, this reads a Screaming Frog/
  equivalent export).

### Step 2 — AI Citation Gap Analysis
- **Objective:** Establish what AI assistants currently say about the client, if anything,
  and who they cite instead. This is the baseline every later phase gets measured against.
- **Repo assets:** `prompts/ai-visibility-gap.md` and `prompts/ai-visibility-triangulate.md`,
  run against `data/ai-visibility/` (or `clients/<client>/data/` once populated) alongside
  `data/gsc/`.
- **Output:** Earned-but-uncited / cited-but-weak-page / winners-to-protect buckets,
  saved as the engagement's baseline report.
- **Cadence:** Once, at engagement start — this is what step 7 tracks changes against.
- **Status:** Built. Requires an AI-visibility export (Semrush, Scrunch, or the
  `fetchers/semrush-ai-visibility.py` fetcher) dropped into `data/ai-visibility/`.

---

## Phase 2 — Structure
*Fixing the foundation before touching a word of copy.*

### Step 3 — Information Architecture & Internal Linking Map
- **Objective:** Map how pages should connect. Isolated pages with no internal links read
  as low-authority to search engines and AI systems alike.
- **Repo assets:** `prompts/internal-linking-map.md`, run against the same
  `internal_all.csv` / `all_inlinks.csv` exports used in step 1B (this workflow depends on
  step 1B having already run).
- **Output:** A linking map / IA recommendation, saved to `clients/<client>/reports/`.
- **Cadence:** Once, early — revisit if step 6 (content gap fill) adds enough new pages to
  change the structure.
- **Status:** Built (depends on step 1B's crawl export).

### Step 4 — Schema & Structured Data Plan
- **Objective:** Identify missing structured data (Organization, Product, FAQ, Article) and
  package it as copy-ready JSON-LD for a developer to drop in.
- **Repo assets:** `prompts/page-reviewer.md` step 6 produces this per-page as part of a
  page review (see the "Schema Recommendation" section of
  `reports/page-review-template.md`). For a site-wide plan rather than per-page, aggregate
  the schema recommendations across all page reviews done in step 5.
- **Output:** JSON-LD snippets + dev ticket notes, either embedded in each page review or
  rolled into a standalone schema plan in `clients/<client>/reports/`.
- **Cadence:** Once per page (via step 5), revisited when new page types are added.
- **Status:** Built, at the page level.

---

## Phase 3 — Create
*Where the five levers get applied.*

### Step 5 — Five-Lever Page Optimization
- **Objective:** The core deliverable — every page scored and fixed against the five-lever
  standard, whether it's one page or fifty.
- **Repo assets:** `prompts/page-reviewer.md` (the workflow) + `config/five-lever-framework.md`
  (the standard being applied) + `reports/page-review-template.md` (the output format).
- **Output:** A scorecard (Pass/Needs Work/Fail per lever), prioritized self-serve vs.
  dev/IT fixes, and rewritten on-page elements (title, meta, H1, answer-first opening,
  FAQ). Saved to `clients/<client>/reports/YYYY-MM-DD-page-review-<page>.md`.
- **Cadence:** Per page, per engagement — this is the workflow you run whenever the ask is
  "review/audit/score this page."
- **Status:** Built. Run `qa/report-checklist.md` before delivery.

### Step 6 — Content Gap Fill
- **Objective:** Where competitors are cited on topics the client doesn't cover at all,
  identify the gap and draft a plan to close it with new pages/sections — not just edits
  to existing ones.
- **Repo assets:** `prompts/ai-demand-briefs.md`, cross-referencing
  `data/ai-visibility/semrush/` (topic volume + real user prompts) against `data/gsc/`
  (validated demand).
- **Output:** A prioritized content brief list — target topic, demand signal, literal
  questions to answer, internal-link siblings, recommended format, new page vs. refresh.
  Saved to `clients/<client>/reports/`.
- **Cadence:** Once per engagement start, then whenever step 7 tracking surfaces a new
  demand signal worth chasing.
- **Status:** Built.

---

## Phase 4 — Measure
*Proving it's working.*

### Step 7 — AI Share-of-Voice Tracking
- **Objective:** Ongoing tracking of how often the client is mentioned/cited across AI
  assistants, so "is this working" has a number behind it instead of a guess.
- **Repo assets:** `prompts/ai-visibility-triangulate.md`, run on a fresh
  `data/ai-visibility/` export each cycle, diffed against the step 2 baseline.
- **Output:** A trend note — confirmed wins (both tools agree), disagreements to
  investigate, engine-coverage gaps — saved dated to `clients/<client>/reports/`.
- **Cadence:** Recurring — monthly is the default cadence for a retainer; confirm actual
  cadence in `clients/<client>/client-facts.md` or `business/contracts.md`.
- **Status:** Built. Treat all AI-visibility numbers as directional (see the prompt's
  caveats) — never state a single-run citation count as stable fact.

### Step 8 — Rank & Traffic Monitoring
- **Objective:** Traditional rankings and organic traffic still get tracked alongside GEO —
  it doesn't replace that measurement.
- **Repo assets:** `prompts/low-ctr-opportunities.md` (GSC + GA4 cross-reference) and
  `prompts/paid-organic-overlap.md` (GSC + Ads cross-reference) for the recurring numbers;
  raw trend pulls from `data/gsc/` and `data/ga4/`.
- **Output:** Prioritized opportunity lists (high-impression/low-CTR pages, paid spend to
  reallocate), saved dated to `clients/<client>/reports/`.
- **Cadence:** Recurring, same cadence as step 7 — the two are usually reported together.
- **Status:** Built.

---

## Phase 5 — Repeat
*Keeping it from going stale.*

### Step 9 — Content Decay Refresh & Reporting
- **Objective:** Catch pages that were accurate a year ago and have quietly gone stale
  (price changes, discontinued products, competitors catching up) before decay costs
  citations. Roll everything into a plain-English report, not a numbers dump.
- **Repo assets:** `prompts/content-decay-refresh.md` — diffs each page's current scorecard
  against its prior review, checks facts against `client-facts.md`'s correction log, and
  pairs with a fresh step 2/7 AI-visibility check for the same pages.
- **Output:** A refresh report per page/batch, plus the recurring rollup report that ties
  steps 7-9 together for the client. Saved to `clients/<client>/reports/`, and run through
  `qa/pre-delivery-checklist.md` before it goes external.
- **Cadence:** Recurring — quarterly is a reasonable default for a content decay sweep;
  confirm against the specific retainer scope.
- **Status:** Built. Depends on a prior page review existing to diff against — pages never
  reviewed before route to step 5 instead.

---

## Cadence summary

| Steps | When they run |
|---|---|
| 1-2 (Audit) | Once, at engagement start |
| 3-4 (Structure) | Once, early — revisited only on major site changes |
| 5-6 (Create) | Per page / per identified gap, ongoing through the engagement |
| 7-8 (Measure) | Recurring on the retainer's reporting cadence (default: monthly) |
| 9 (Repeat) | Recurring, less frequently (default: quarterly) |

A single page-review engagement is effectively step 5 alone, with steps 1-2 done
informally (read the page and the client-facts, don't assume a full crawl happened).

## Gaps — not yet built
Honest state as of this writing, so nobody assumes automation that isn't there:
- **Step 1A** is entirely manual — a browser visit to an external grader tool, no repo
  fetcher or saved-API integration for it.
- **Step 1B** still has no in-repo crawler — it reads a Screaming Frog (or equivalent)
  export rather than pulling one itself. A Screaming Frog license (paid tier) is needed for
  crawls over 500 URLs; the free tier works for smaller sites.
- **Steps 1B and 3** both key off crawler export column names (`Internal All`,
  `All Inlinks`). If the crawl tool changes (different tool than Screaming Frog, or a
  future Screaming Frog export schema change), re-check the column names the prompts
  reference still match.
- No other steps have a known gap right now.

If a step's tooling changes or a new gap turns up, update that step's "Status" line and
this section together — don't let this doc drift from what's actually runnable.
