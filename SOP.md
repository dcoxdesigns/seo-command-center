# Small Factory 5 — Operating SOP

How to actually run the practice, day to day. Written for someone who has
never touched this repo before. For the *why* behind each step, see
`config/nine-step-workflow.md` — this doc is the *how*.

---

## 0. One-time setup

- Clone this repo and `tools/ai-visibility-tracker`'s sibling `smallfactory5-site` repo.
- In this repo: `cp .env.example .env` in `tools/page-grader/` and
  `tools/ai-visibility-tracker/`, then fill in real keys (ask David for them —
  never commit `.env`, it's gitignored on purpose).
- You'll need: an `ANTHROPIC_API_KEY` (used by both the Page Grader and the
  AI Visibility Tracker's Recommendation Rate classification), and for the
  AI Visibility Tracker, `OPENAI_API_KEY` / `PERPLEXITY_API_KEY` /
  `GEMINI_API_KEY` (missing ones just get skipped, not fatal).
- Screaming Frog is only needed for Site Audits (multi-page jobs), not single
  page reviews. Free tier covers sites under 500 URLs.
- The client-facing web tool lives at `smallfactory5.com/tools/page-review/`,
  protected by a single admin password (ask David — don't ask him to paste it
  in chat, have him tell you directly).

---

## 1. Starting a new client

1. Copy the template folder: `cp -r clients/_template clients/<client-slug>`
2. Fill in `clients/<client-slug>/client-facts.md` — domain, goals, brand
   terms, competitors, correction log. Read this file fresh every time you
   work on this client; don't rely on memory of a past session.
3. If tracking AI visibility for this client (see Step 4), also fill in
   `clients/<client-slug>/ai-visibility-tracker.json`.

---

## 2. Running a single Page Review (the most common job)

Two ways to run it — pick based on whether the client needs to see it.

**A — Web tool (use this whenever a client will see the result):**
1. Go to `smallfactory5.com/tools/page-review/`, log in with the admin
   password.
2. Fill in **Client Name** (must exactly match the name used in that
   client's `ai-visibility-tracker.json`, if they have one — see Step 4) and
   the **Page URL**.
3. Click Run. Takes up to ~60 seconds.
4. Copy the **shareable link** it generates and send that to the client —
   never send them the admin URL or password. The link is permanent and
   read-only; they can't trigger new runs from it.

**B — CLI (internal use, no client-facing link needed):**
```bash
cd tools/page-grader
python run.py --url https://example.com/page --run --client <client-slug>
```
Saves to `clients/<client-slug>/reports/`. Leave off `--client` to just print
to the terminal instead of saving. Always dry-runs (no API call, no cost)
unless you pass `--run`.

Either way: run `qa/report-checklist.md` against the output before it goes
external.

---

## 3. Running a Site Audit (bigger, multi-page job)

This is Steps 1B/3 of the nine-step workflow — do this before individual
page reviews on a new full-site engagement.

1. Crawl the site in Screaming Frog. Export **Internal All** and **All
   Inlinks**.
2. Drop both exports into `clients/<client-slug>/data/crawl/`.
3. Run `prompts/site-crawl-baseline.md` for the technical baseline report,
   and `prompts/internal-linking-map.md` for the linking/IA recommendation.
4. Then run individual Page Reviews (Step 2 above) for the priority pages
   the baseline surfaces.

---

## 4. Tracking AI visibility (Citability Index)

Opt-in per client — only set this up if the engagement includes ongoing
tracking, not for one-off page reviews.

1. Add `clients/<client-slug>/ai-visibility-tracker.json` (copy the shape
   from `clients/_template/ai-visibility-tracker.json` — client name, domain,
   brand variants, a handful of realistic buyer-phrased prompts).
2. Run it:
   ```bash
   cd tools/ai-visibility-tracker
   python run.py --client <client-slug>        # dry run first, check the plan
   python run.py --client <client-slug> --run   # real run, spends API money
   ```
3. Generate the client-facing report:
   ```bash
   python client_report_cli.py --client <client-slug> --html
   ```
   Saves a self-contained HTML file to `clients/<client-slug>/reports/` —
   open it in a browser and print to PDF if you need an attachable document
   instead of a link.
4. Push the latest score so the Page Review Tool can show it automatically
   on that client's page reviews:
   ```bash
   python export_citability.py --client <client-slug>
   ```
   This requires the same Redis credentials as `smallfactory5-site` — copy
   them from that repo's `.env.local`/`.env.development.local` into this
   tool's `.env` once, ask David if you don't have them.
5. Repeat monthly (default cadence) for an active retainer.

---

## 5. Where everything lives

- `clients/<slug>/client-facts.md` — read before every task on that client.
- `clients/<slug>/data/` — read-only inputs (crawl exports, GSC/GA4 pulls).
- `clients/<slug>/reports/` — everything you deliver, dated.
- `config/` — the standards being applied (five-lever framework, brand
  voice, nine-step workflow) — don't restate these in output, apply them.
- `qa/` — checklists. Run the relevant one before anything ships externally.

---

## 6. Rules that don't bend

- Never commit `.env` or any real API key/password. `.gitignore` already
  blocks `.env*` — don't override that.
- Never invent a client fact, competitor claim, or statistic. If you don't
  have a real number, say so or leave it null — don't guess.
- Never write directly to a live client site. Everything here is a draft or
  a dev-ready spec, not a deployment.
- If a request doesn't specify which client, ask. Don't guess and apply the
  wrong client's facts to a report.
- Sending anything to a client, or deleting a client folder, needs a human
  sign-off first — don't do either unprompted.
