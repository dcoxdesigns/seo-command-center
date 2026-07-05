# QA checklist — run before any report is "done"

Trust but verify. Walk this before a report leaves `reports/`.

## Numbers
- [ ] Every figure traces to a named source file in `data/` and a stated date range.
- [ ] Any number that can't be tied to a source is labeled **needs human review**, not stated as fact.
- [ ] Totals and percentages recomputed, not carried over from the model's first pass.

## Logic
- [ ] Cross-source claims (e.g. paid-organic overlap, AI-gap) actually join on the same query/URL — not two unrelated rows that happen to look similar.
- [ ] AI-visibility claims are hedged as directional; no single-run citation count stated as stable truth.
- [ ] No cannibalization/consolidation recommendation without showing the competing URLs.

## Output
- [ ] Findings come before recommendations; required actions are prioritized.
- [ ] No hallucinated client specifics (page paths, product names) that aren't in `config/` or `data/`.
- [ ] Plain language a strategist can hand to a client without rewriting.

## Sign-off
- [ ] A human read the whole thing. The strategist's judgment is the last gate, not the model's.
