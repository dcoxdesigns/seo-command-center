# Small Factory 5 — Slide Deck Style Guide

The "light industrial / technical blueprint" visual style used for Small Factory 5
portfolio and process decks (the kind built in NotebookLM and embedded on the website).
This is the visual counterpart to `brand-voice.md` — that file covers how SF5 sounds in
writing, this one covers how it looks in a slide deck.

## The short version
**A cream engineering-graph-paper background, navy blueprint linework, one burnt-orange
accent color, bold condensed all-caps headlines, and dimension-line/corner-tick framing
on every slide — like a mechanical blueprint that happens to be explaining a GEO
concept instead of a machine part.**

## Color palette
- **Background:** Cream / aged paper (`#F3EEE1` – `#EDECE4`), always with a faint graph-paper
  grid visible underneath the content, not solid flat color.
- **Primary ink / structure:** Navy blueprint blue (`#1B2A44` – `#2C4870`). Used for headlines,
  corner tick marks, dimension lines, primary diagram linework, and dark panel fills.
- **Accent:** Burnt orange / signal orange (`#C15A2E` – `#F2A900`). Used sparingly — for the
  single most important number on a slide, arrows showing data flow, tag/label boxes, and
  "this is the point" callouts. Never used as a second competing headline color; one accent
  only.
- **Supporting neutrals:** White panels/cards for content blocks that sit on top of the cream
  background, light grid-line gray (`#E3DCC8`) for the graph paper texture itself, dark
  charcoal (`#202020`) for body text.
- **Contrast rule:** Never navy text on orange or orange text on navy for body copy — the
  accent color is for shapes, numbers, and short tags, not paragraphs.

## Typography
- **Headlines:** Bold, heavily condensed, all-caps, sans-serif — think Big Shoulders Display
  or Arial Black. Headlines are large and blunt, never a light or thin weight.
- **Body copy:** Clean, plain sans-serif (Arial / IBM Plex Sans equivalent), sentence case,
  restrained size relative to the headline.
- **Labels/tags/technical annotations:** Monospace (IBM Plex Mono equivalent), small,
  letter-spaced, all-caps — used for dimension labels, module tags ("MODULE A-01:"), and
  status callouts ("STATUS: OPTIMIZED"), never for headlines or body paragraphs.
- **Hierarchy:** One headline per slide, one short subtitle sentence under it, then the
  visual/diagram carries the rest. Avoid dense paragraph blocks — this style reads as
  engineering documentation, not a memo.

## Framing and structure devices
- **Corner tick marks:** Every slide has small navy right-angle marks in all four corners,
  like a technical drawing's frame registration marks.
- **Dimension lines:** Thin lines with arrowheads and a measurement label, used along slide
  edges or around key diagram elements — purely decorative/thematic, not literal
  measurements.
- **Tag boxes:** Small solid-navy rectangles with white monospace all-caps text, used as
  section labels or category tags (e.g., "SYSTEM PROPOSAL // PORTFOLIO SUPPLEMENT").
- **White content cards:** Information sits on crisp white rectangles/panels laid over the
  cream background, giving a "part sitting on a workbench" feel rather than a flat slide.
- **Grid visibility:** The graph-paper grid should be faintly visible in open background
  space on every slide — it's a texture, not just a color.

## Iconography and illustration
- Line-art only, navy on cream (or white), no flat-color icon fills except the orange
  accent where something needs to stand out.
- Recurring motifs: gears, factory/assembly-line diagrams, pipe-and-flow diagrams (data
  moving through a system), blueprint-style exploded diagrams, dimension-line callouts on
  illustrated objects.
- Diagrams should look hand-drafted-but-precise — technical, not cartoonish. Avoid rounded/
  cute illustration styles; this is closer to a patent drawing or an assembly manual.
- Data-flow diagrams (arrows connecting boxes) use orange arrows specifically — navy is
  for structure, orange is for movement/emphasis.

## Slide-type patterns
- **Cover slide:** Large navy headline, one-sentence orange-accented subtitle, a small
  info-box table (bottom right is typical) with prepared-for/architect/location-style
  metadata, plus a tag box top-left.
- **Comparison slide:** Two-column layout, "before/isolated/traditional" on the left in a
  muted or gray-orange treatment, "after/unified/new" on the right in navy/orange — same
  shape repeated on both sides so the eye can diff them directly.
- **Stat/metric slide:** A 2x2 or row grid of white module cards, each with a small navy
  label, one huge orange number, and a short black caption underneath.
- **Process/wheel slide:** A central navy gear or hub labeled with the throughline concept,
  radiating spokes/arrows out to individually labeled phase boxes.
- **Quote/closing slide:** Large centered italic navy statement in quotation marks, minimal
  supporting content, corner ticks still present, contact info in a simple white box below.

## What to avoid
- Flat, modern SaaS-style illustration (rounded blobs, gradient mesh backgrounds, cute
  mascots) — this breaks the blueprint conceit entirely.
- More than one accent color competing for attention on the same slide.
- Dense paragraph text — if a slide needs more than 2-3 sentences of prose, it's the wrong
  slide type; split it or convert it into a labeled diagram/table instead.
- Fabricated or unverifiable stats presented as fact. This style makes numbers look highly
  authoritative (large, bold, orange) — that's exactly why every number placed on a slide in
  this style needs to be real and sourced, not filler. See `brand-voice.md`'s "numbers over
  adjectives" rule and the QA checklists in `qa/` before anything with a specific claim on
  it goes out the door.
