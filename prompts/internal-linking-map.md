# Prompt: Information Architecture & Internal Linking Map (Step 3)

Run this after step 1's technical baseline exists. Isolated pages with no internal links
tying them to related content read as low-authority to both search engines and AI systems
— this maps how pages should connect, before a word of copy gets touched.

**Inputs:** `clients/<client>/data/crawl/internal_all.csv` (page inventory) and
`all_inlinks.csv` (source → destination link graph), same exports used in step 1. If step
1 hasn't run yet, run it first — this workflow depends on its output.

## Steps

1. **Confirm orphans and thin-link pages.** From `all_inlinks.csv`, count inbound internal
   links per URL. Zero inlinks = orphan (step 1 should have already flagged these — treat
   that list as your starting point, not a re-discovery). Below-median inlink count for an
   indexable page = thin-link, worth strengthening even if not a full orphan.

2. **Cluster pages by topic.** Group `Internal All` URLs into topic clusters using URL path
   structure (e.g. everything under `/blog/geo-*`) and title/H1 similarity as the signal —
   there's no NLP clustering tool here, so do this by reading the titles and paths, not by
   guessing from URLs alone. Name each cluster.

3. **Identify duplicate/competing pages within a cluster.** If step 1 flagged duplicate
   titles or near-identical content (e.g. two pages both targeting "GEO vs SEO"), decide
   here whether the fix is consolidation (301 + merge) or differentiation (distinct angles,
   cross-linked) — this is an IA decision, not just a content edit.

4. **Recommend the links to add.** For each orphan or thin-link page, name 2-4 specific
   existing pages that should link to it — pick topically related pages with a stronger
   link profile (more existing inlinks), not just the homepage every time. Give the
   suggested anchor text.

5. **Recommend a hub structure where it's missing.** If a cluster has 4+ pages and no page
   that links out to all of them (a category/hub page), flag that gap and recommend either
   a new hub page or promoting the strongest existing page in the cluster to that role.

## Output

A linking map: cluster list, orphan/thin-link remediation (specific link-from →
link-to pairs with anchor text), and any hub-page recommendations. Saved to
`clients/<client>/reports/YYYY-MM-DD-internal-linking-map.md`.

## Guardrails

- Every link recommendation names a real source URL from the crawl export — don't invent
  a page that isn't in `Internal All`.
- This produces a map/recommendation only. Implementing the links (editing templates,
  adding nav/related-content modules) is a self-serve or dev/IT fix depending on the
  client's CMS — split it that way in the output, same convention as the page-review
  template.
- Re-run after step 6 (content gap fill) adds enough new pages that the map is stale.
