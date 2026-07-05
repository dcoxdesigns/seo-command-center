# Prompt: Content briefs from AI demand

Use the AI-visibility data as a *content-demand* source, not just a scoreboard. Read `data/ai-visibility/semrush/` (topics + prompts) and cross-reference `data/gsc/`.

**1. Size the gaps by AI demand.** From the Semrush topics file, surface topics with high `topic_volume` but low `mentions` / `cited_pages` — high demand, little presence. Rank them. Flag any that also have GSC impressions (validated demand) versus AI-only demand (directional). Drop topics that aren't a fit for `config/`'s priority_sections.

**2. Pull the literal questions.** From the Semrush prompts file, list the actual prompts people ask the engines for each priority topic. These are your FAQ entries, H2s, and the angle the page has to answer. Use the real phrasing, not a paraphrase.

**3. Reverse-engineer what gets cited.** From the cited-pages file, note which existing pages get pulled into answers and how they're structured (answer-first, list, comparison). New briefs should match that extractable shape.

**4. Output a prioritized brief list.** For each opportunity: target topic, demand (volume + which signals confirm it), the literal questions to answer, internal-link siblings, the recommended format, and whether it's a new page or a refresh.

**Caveat:** Semrush topic volumes are their dataset and the prompts are sampled and engine-skewed (Gemini-heavy). Treat as directional demand and validate against GSC before committing real effort. The value is pairing AI demand with traditional demand, not trusting either alone.
