# Workflow: Content Decay Refresh & Reporting (Step 9)

Pages that were accurate a year ago quietly go stale — prices change, products get
discontinued, competitors catch up. Run this on a recurring basis (quarterly by default;
confirm against the client's actual retainer cadence) to catch decay before it costs
citations, and roll it into a plain-English report.

## Before starting
1. Confirm which client this is for. If not stated, ask — do not guess.
2. Read `clients/<client>/client-facts.md` in full, including the correction log — this is
   where "the client discontinued X" or "the price changed to Y" type facts should live.
3. List every prior report in `clients/<client>/reports/` matching `*page-review*.md`,
   sorted by date. These are your prior scorecards to diff against.

## Steps
1. **Pick the batch.** Default to pages last reviewed more than one reporting cycle ago
   (90+ days for a quarterly cadence). If this is the first decay pass for this client,
   every previously-reviewed page is in scope.
2. **Re-pull each page's current content.** Fetch the live URL — don't reuse the old
   review's cached text. If a page 404s or redirects, that's a finding on its own (flag it,
   don't silently skip it).
3. **Re-run the five-lever scorecard** (`config/five-lever-framework.md`) on the current
   content and diff it against the prior review's scorecard. Call out any lever that
   dropped (e.g. Factual Density: Pass → Needs Work because a stat is now outdated).
4. **Check facts against `client-facts.md` and the correction log specifically.** Flag any
   on-page claim that contradicts a known change (discontinued product, changed pricing,
   old team member, expired certification, stale "as of" date).
5. **Check competitive standing.** Note if a competitor now covers this topic more
   thoroughly than when it was last reviewed — pair with a quick check of
   `prompts/ai-visibility-gap.md` output for the same URL if a recent AI-visibility export
   exists, to see if citation status changed since the baseline.
6. **Write the refresh recommendation.** Same self-serve vs. dev/IT split as a normal page
   review — what needs updating, not just "this is stale."
7. **Roll the batch into one recurring report** rather than one file per page (unless a
   single page needs urgent, isolated attention) — this is meant to read as a periodic
   health check, not a stack of unrelated one-offs.

## Output
A dated decay report per batch: which pages were checked, what changed since last review
(scorecard deltas, stale facts, competitive shifts), and prioritized refresh actions.
Saved to `clients/<client>/reports/YYYY-MM-DD-content-decay-refresh.md`. Run
`qa/report-checklist.md` before it's considered done, `qa/pre-delivery-checklist.md`
before it goes external.

## Guardrails
- Never mark a page "decayed" on a vague feeling — every flag ties to something concrete:
  a scorecard regression, a fact contradicting `client-facts.md`, a dead link, or a
  documented competitive change.
- If a page was never reviewed before (no prior scorecard exists), this isn't a decay
  check — it's a first review. Route it to `prompts/page-reviewer.md` (step 5) instead.
- Don't invent a "before" state if the prior report is missing or incomplete — say the
  comparison isn't possible and score the page fresh instead.
