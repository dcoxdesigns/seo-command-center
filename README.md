# SEO Command Center

Starter project for the SMX Master Class **"Turn Claude Code into Your SEO Command Center"** (Will Scott, Search Influence — online, June 25, 2026).

This is the command-center architecture from the class — no client data, no clutter. Copy it and run your own SEO operations inside it.

## Start here

```bash
# clone it (or click "Use this template" / download the ZIP)
git clone https://github.com/willscott-v2/seo-command-center.git
cd seo-command-center
```

Then open the folder in Claude Code (or Cursor, Codex, Antigravity, Copilot — it ships an `AGENTS.md` they all read), copy `config/client.example.yml` to a real config, drop your CSV exports into `data/`, and ask away. Sample data ships so it works offline before you connect anything.

## Structure

```
config/            one file per client/site (config/client.example.yml to copy)
data/              performance exports — read-only inputs
  gsc/  ga4/  ads/  ai-visibility/  exports/
fetchers/          optional API-pull scripts (CSV path works without these)
prompts/           reusable named analysis prompts
reports/           deliverables land here, dated + client-named
qa/                verification checklists — run before a report is "done"
AGENTS.md          the agent contract (works in Claude Code, Cursor, Antigravity, Copilot, Codex)
CLAUDE.md          pointer to AGENTS.md for Claude Code
```

## Running the demo

1. Open this folder in your tool of choice (Cursor for the live demo; the same setup runs in Antigravity or Copilot).
2. Copy `config/client.example.yml` to a real config and fill it in.
3. Drop CSV exports into the matching `data/` subfolder, or wire up a fetcher.
4. Ask a cross-source question, or run one of the `prompts/`.
5. Review the output, run the QA checklist, then ship from `reports/`.

Sample data ships in `data/` so the demo works offline with nothing connected.
