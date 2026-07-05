# Prompt: High-impression / low-CTR pages

From `data/gsc/`, find queries with above-median impressions but below-median CTR for their position band. These are pages earning visibility but losing the click — usually a title/meta or intent-match problem.

For each, pull the matching landing page from `data/ga4/` if one exists and note engagement rate and conversions so we know whether fixing CTR is worth it. Output a prioritized list: query, impressions, CTR, position, the likely cause, and a specific title/meta rewrite suggestion. No unsourced numbers.
