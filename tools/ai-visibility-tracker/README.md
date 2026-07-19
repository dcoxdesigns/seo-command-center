# SF5 AI Visibility Tracker

Internal tool — tracks whether SF5 client brands/domains get mentioned or
cited in AI-generated answers across ChatGPT, Perplexity, and Gemini.
Supplements manual spot-checking and Otterly.ai for SF5's own client
tracking. Not a client-facing product. No third-party Python packages —
standard library only, same convention as `fetchers/`.

## The metric: Citability Index

A 0-100 score per client per platform, ties directly to the Citability lever:

```
Citability Index = (Mention Rate x 40) + (Citation Rate x 60)
```

Citation is weighted higher than mention — being cited as a source means the
page itself did the work, not just brand-name recognition.

| Score | Band |
|---|---|
| 0-25 | Low visibility |
| 26-50 | Emerging |
| 51-75 | Solid |
| 76-100 | Strong |

## Setup

```bash
cd tools/ai-visibility-tracker
cp .env.example .env
# fill in real API keys in .env — OPENAI_API_KEY, PERPLEXITY_API_KEY, GEMINI_API_KEY
```

Missing a key just skips that platform (with a warning) — the run still
covers whichever platforms have keys set.

## Enabling tracking for a client

Add `clients/<slug>/ai-visibility-tracker.json` (copy the shape from
`clients/_template/ai-visibility-tracker.json`):

```json
{
  "client": "Example Manufacturing Co",
  "domain": "examplemfg.com",
  "brand_variants": ["Example Manufacturing", "Example Mfg", "ExampleMfg Co"],
  "prompts": [
    "best industrial hose manufacturer for automotive",
    "who makes reliable rubber hoses for factories",
    "top B2B hose suppliers"
  ]
}
```

Prompts should mirror realistic buyer queries, not branded searches — pull
ideas from the client's actual SEO/keyword data where available. Tracking is
opt-in per client: a client with no `ai-visibility-tracker.json` is just
skipped, nothing breaks.

## Running it

```bash
python run.py                       # dry run — shows the plan and a rough cost estimate, no API calls
python run.py --run                 # actually calls the APIs, spends money, stores results
python run.py --run --client acme   # only one client
```

Always dry-runs by default — same safety pattern as
`fetchers/semrush-ai-visibility.py`. Every raw API response is saved to
`clients/<slug>/data/ai-visibility-tracker/<run-timestamp>/` before parsing,
so a bad parse or a future scoring-logic change never loses data.

## Reporting

```bash
python report_cli.py                # every tracked client
python report_cli.py --client acme  # one client
```

Shows the latest Citability Index (blended + per-platform), its band, and the
trend vs. the previous run. A client is flagged in the output if their
blended index dropped 15+ points or fell into a lower band since last time —
see `ALERT_DROP_THRESHOLD` in `tracker/citability.py` to tune that.

## Known gaps / things to verify before relying on this

- **Platform API shapes are not live-tested.** No API keys were available
  while building this — the ChatGPT, Perplexity, and Gemini integrations
  (`tracker/platforms/*.py`) are built from each provider's documented
  request/response shape, not verified against a real call. Run one client
  with one prompt on each platform first and check the output before
  trusting a full run. If a platform's parsing breaks, the raw HTTP response
  is still logged to `clients/<slug>/data/ai-visibility-tracker/`, so nothing
  is lost — only the detection step needs a fix and a re-parse.
- **Copilot is out of scope for v1** — no clean API without a paid scraping
  service.
- **No client-facing dashboard** — this is an internal reporting tool.
- **No historical backfill** — tracking starts from whenever this first runs
  for a client.
- **Position-in-response detection** (early/mid/late) is not built — flagged
  in the original brief as an optional v1.1 refinement, not required for v1.

## Storage

Single SQLite file at `data/tracker.db` (gitignored — real client data, not
source). Schema:

```sql
runs(id, client, platform, prompt, timestamp, mentioned, cited, citation_urls, raw_response_path)
```

`timestamp` is shared by every row from the same `run.py` invocation, so
grouping by timestamp is how reporting distinguishes "this run" from "a prior
run" for the trend line.
