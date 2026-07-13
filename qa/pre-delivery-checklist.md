# Pre-Delivery QA Checklist

Run through this before any report or deliverable leaves the repo and goes to a client.
This is a manual check — read it and verify, don't just assume it passes.

## Client accuracy
- [ ] Correct client name used throughout — no leftover references to a different client
      (check for copy-paste bleed from a previous report)
- [ ] Every fact/claim about the client matches `clients/<client>/client-facts.md`
- [ ] No off-limits claims from the client's list appear anywhere in the deliverable
- [ ] Brand voice guidance for this specific client was respected (not Small Factory 5's
      own voice bleeding into client-facing recommendations about their own copy)

## Factual integrity
- [ ] No invented statistics, competitor claims, or citations — everything traces back to
      an actual source (client-facts.md, a real fetch/search, or the page itself)
- [ ] Any competitive claim ("Competitor X does Y") is sourced, not assumed
- [ ] Schema/technical recommendations are accurate to current best practice, not outdated

## Voice and tone
- [ ] Written in Small Factory 5's brand voice (`config/brand-voice.md`) — analytical,
      direct, first person "I," no corporate filler
- [ ] No overpromising (guaranteed rankings, guaranteed AI citations)

## Format and delivery
- [ ] Self-serve vs. dev/IT fixes are clearly split
- [ ] Saved to the correct client's `reports/` folder with a dated filename
- [ ] If this is going externally (email, PDF, doc), formatted appropriately — ask before
      finalizing if unsure whether it should be a Word doc/PDF vs. plain markdown

## Final gut check
- [ ] Would I be comfortable if the client screenshotted this and shared it publicly?
- [ ] Does this actually help them, or is it padded to look more thorough than it is?
