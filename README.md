# SEO Command Center

Starter project for the SMX Master Class **"Turn Claude Code into Your SEO Command Center"** (Will Scott, Search Influence — online, June 25, 2026).

This is the command-center architecture from the class — no client data, no clutter. Copy it and run your own SEO operations inside it.

## Start here

```bash
# clone it (or click "Use this template" / download the ZIP)
git clone https://github.com/willscott-v2/seo-command-center.git
cd seo-command-center
```

Then open the folder in Claude Code (or Cursor, Codex, Antigravity, Copilot — it ships an `AGENTS.md` they all read), copy `clients/_template/` to `clients/<your-client>/`, fill in `client-facts.md`, and drop your CSV exports into that client's `data/`. Sample data ships in the legacy top-level `data/` so it works offline before you connect anything.

## Structure

```
clients/<name>/     per-client workspace (copy clients/_template/ to start one)
  client-facts.md      domain, goals, brand terms, competitors, notes
  data/                that client's performance exports — read-only inputs
  reports/             that client's deliverables, dated
config/             legacy: one file per client/site (config/client.example.yml to copy)
  nine-step-workflow.md   the operational SOP every engagement runs through
  five-lever-framework.md the scoring standard applied per page (step 5)
  methodology.md          long-form explanation of both, for training/client walkthroughs
data/               legacy: shared performance exports — read-only inputs
  gsc/  ga4/  ads/  ai-visibility/  crawl/  exports/
fetchers/           optional API-pull scripts (CSV path works without these), shared across clients
prompts/            reusable named analysis prompts, shared across clients
reports/            legacy: shared deliverables, dated + client-named
qa/                 verification checklists, shared across clients — run before a report is "done"
AGENTS.md           the agent contract (works in Claude Code, Cursor, Antigravity, Copilot, Codex)
CLAUDE.md           pointer to AGENTS.md for Claude Code
```

## Running the demo

1. Open this folder in your tool of choice (Cursor for the live demo; the same setup runs in Antigravity or Copilot).
2. Copy `config/client.example.yml` to a real config and fill it in.
3. Drop CSV exports into the matching `data/` subfolder, or wire up a fetcher.
4. Ask a cross-source question, or run one of the `prompts/`.
5. Review the output, run the QA checklist, then ship from `reports/`.

Sample data ships in `data/` so the demo works offline with nothing connected.
