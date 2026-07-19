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

### Sampling methodology

A single query against a single model on a single day is a sample size of
one — AI answers vary run to run, and web search results shift underneath
the same prompt. So every prompt is called **3 times per platform, per run**
(`REPLICATES_PER_PROMPT` in `tracker/runner.py`), and Mention/Citation Rate
are the average across those 3 calls, not a single pass/fail. All 3 raw
responses are stored, not just the aggregate — that's the receipts if a
client questions a score, and it's what lets the client report show "cited 2
of 3 times" instead of a flattened yes/no.

This also means the actual API call volume — and cost — is **3x** whatever a
naive prompts × platforms count would suggest. The dry-run output in `python
run.py` reflects the real, replicated total, not a pre-sampling estimate.

Run the full battery on a defined cadence (monthly is the suggested default)
so clients see a trend, not just a snapshot.

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
python report_cli.py                # every tracked client — quick internal check
python report_cli.py --client acme  # one client
```

Shows the latest Citability Index (blended + per-platform), its band, and the
trend vs. the previous run. A client is flagged in the output if their
blended index dropped 15+ points or fell into a lower band since last time —
see `ALERT_DROP_THRESHOLD` in `tracker/citability.py` to tune that.

### Client-facing report (printable/emailable)

```bash
python client_report_cli.py --client acme            # saves to clients/acme/reports/
python client_report_cli.py --client acme --stdout    # print instead of saving
```

Generates a Markdown report in the same house style as
`reports/page-review-template.md` — summary, Citability Index breakdown,
a per-prompt x per-platform matrix (showing "Cited 2/3" style results, not a
flattened binary), a **"Who's Getting Cited Instead"** table, and a
methodology disclaimer explaining CI results come from providers' grounded
APIs, not the consumer chat apps, and are a directional benchmark rather than
a guarantee of any one user's live session. The "Who's Getting Cited Instead"
table pulls from every citation URL each platform actually returned (not just
the ones matching the client) — the same competitive-gap question step 2 of
the nine-step process (AI Citation Gap Analysis) asks manually, automated.

## Known gaps / things to verify before relying on this

- **Perplexity is live-verified** — tested against a real call, request and
  response parsing both confirmed correct. **ChatGPT and Gemini are still
  unverified** — built from each provider's documented request/response
  shape, no key was available to test either one live. Run one client with
  one prompt on each before trusting a full run. If a platform's parsing
  breaks, the raw HTTP response is still logged to
  `clients/<slug>/data/ai-visibility-tracker/`, so nothing is lost — only the
  detection step needs a fix and a re-parse.
- **If you write test/scratch scripts against this tool, override the DB
  path first**: `export AI_TRACKER_DB_PATH=/tmp/test.db`. `data/tracker.db`
  is real client data — a test script that deletes "its" database on cleanup
  will delete that file unless you point it elsewhere first. (Learned this
  one directly: an early test script wiped real run data this way. Recovered
  it from the raw JSON logs, which is exactly why those get saved before
  anything is parsed — but better to just not repeat it.)
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
runs(id, client, platform, prompt, timestamp, replicate, mentioned, cited, citation_urls, raw_response_path)
```

`timestamp` is shared by every row from the same `run.py` invocation, so
grouping by timestamp is how reporting distinguishes "this run" from "a prior
run" for the trend line. `replicate` (1-3) distinguishes the repeated calls
the sampling methodology makes for the same prompt within that run.
