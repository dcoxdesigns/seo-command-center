# fetchers/

Optional scripts that pull data into `data/` via API. **The class works without them** — the CSV path (export from GSC/GA4/Ads/your AI-visibility tool, drop into the matching `data/` subfolder) is the lower-friction default, and the one to demo when API access isn't available.

When you do add a fetcher:
- One script per source (`gsc.py`, `ga4.py`, `ads.py`, `ai-visibility.py`).
- Write output into the matching `data/<source>/` folder as CSV or JSON.
- Read credentials from `.env` (gitignored). Never hardcode keys.
- The agent should prefer a fetcher when one exists, and fall back to whatever CSVs are already in `data/` when it doesn't.

API notes worth knowing for the demo:
- **GSC** and **GA4** have official APIs (OAuth / service account).
- **Google Ads** API needs a developer token; the search-terms CSV export is the fast path.
- **AI visibility** — Scrunch, Semrush AI Visibility, and Otterly export CSV/JSON. Bing Webmaster Tools is the only first-party AI-citation source (Copilot/Bing), CSV export, no API yet.
- **Site crawl** (step 1/3 of `config/nine-step-workflow.md`) is export-only, no fetcher —
  Screaming Frog (or equivalent) exports `Internal All` and `All Inlinks` CSVs into
  `data/crawl/`. Screaming Frog does have a CLI for scheduled/headless crawls if that's
  ever worth automating, but there's no API to pull results remotely.
