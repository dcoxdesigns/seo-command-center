# SF5 Report → HTML

Converts an SF5 markdown report — Page Review, Site Audit, or anything else
saved to `clients/<name>/reports/` — into a branded, self-contained HTML
file. Same treatment as the AI Visibility Tracker's client reports: single
file, SF5 logo embedded inline, opens in any browser, prints/exports to PDF
cleanly, safe to attach directly to an email. No third-party dependency —
hand-rolled markdown parser, matching the rest of this repo's `tools/`
convention.

## Usage

```bash
python tools/report-to-html/render.py clients/acme/reports/2026-07-19-page-review-homepage.md
# -> clients/acme/reports/2026-07-19-page-review-homepage.html

python tools/report-to-html/render.py path/to/report.md --out custom-name.html
```

## What it handles

The markdown subset actually used across SF5's report templates: headers
(`#`-`######`), horizontal rules, tables, ordered and unordered lists,
blockquotes, fenced code blocks (for schema/JSON snippets), and inline
bold/italic/code/links. It's a hand-rolled parser tuned to
`reports/page-review-template.md`'s exact structure — not a general-purpose
Markdown implementation, so unusual syntax outside that template (nested
lists, tables with merged cells, etc.) isn't guaranteed to render correctly.

## Why plain Markdown isn't enough

A `.md` file only renders images/tables/formatting correctly in a
markdown-aware viewer. Pasted into an email body or opened in a plain text
view, a client sees literal `**bold**` and `| table | syntax |` — not a
formatted report. The HTML output here is what should actually get sent.

## Other customer-facing documents not yet covered

`business/services-agreement-template.md` (the actual contract sent to
clients) is customer-facing too, but wasn't converted — a signed agreement
typically wants a clean printable Word/PDF for an e-signature flow, not a
colorful branded page, so it's a different kind of document with a different
right answer. Flagging it here rather than silently skipping it.
