# Prompt: Triangulate AI visibility across two tools + GSC

Cross-reference three sources for the same brand:

1. **Semrush AI Visibility** — the JSON in `data/ai-visibility/semrush/` (overview, topics, prompts, cited pages). Source: clickstream + Google's keyword dataset. Engines: ChatGPT, Gemini, Google AI Mode, Google AI Overview. Note it skews heavily to Gemini / Google surfaces.
2. **A monitoring tool (Scrunch)** — `data/ai-visibility/scrunch/*.csv`. Prompt-panel method. Adds **Perplexity and Copilot** coverage Semrush does not report.
3. **Search Console** — `data/gsc/` for the organic rank picture on the same queries/topics.

Produce three buckets. Cite the source file for every claim.

**1. Both tools agree we're cited (high confidence).** Queries/pages where Semrush *and* Scrunch both show citations. These are your confirmed wins — protect them. Note the page.

**2. The tools disagree (investigate, don't report as fact).** Cited in one tool but not the other, or strong in one engine and absent in another. Usually this is engine-coverage difference, not a contradiction. Flag which engine each tool is seeing, and hedge the number.

**3. Engine-coverage gaps.** Where Scrunch shows ChatGPT/Perplexity/Copilot citations that Semrush can't see, and where Semrush's Gemini/AI-Overview view adds what Scrunch misses. The point: neither tool is the whole picture.

Then connect to organic: any topic with high demand (Semrush `topic_volume`) but low mentions across both tools is a **content opportunity**, not just a tracking gap. Surface the top few.

**Treat all of this as directional — a wind sock, not GPS.** Single-run citation counts vary; two tools on the same brand will not match. The value is the triangulation, not any one number. Bing Webmaster Tools is the only first-party Copilot/Bing citation source if you want to ground that engine specifically.
