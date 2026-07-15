# The Small Factory 5 Methodology
## Five Levers, Nine Steps — Complete Process Reference

This is the full, long-form explanation of how Small Factory 5 works: the standard every
page is judged against (the Five Levers) and the process every engagement runs through
(the Nine Steps). It exists to answer "why do we do it this way" in depth — for training,
for onboarding, and as the reference to return to when a client asks "walk me through
your process" and a one-page summary isn't enough.

This is the **long-form companion** to two shorter, operational files:
- `config/five-lever-framework.md` — the quick-reference scoring checklist, used during
  an actual page review.
- `config/nine-step-workflow.md` — the tool map, showing which prompt/fetcher/checklist
  implements each step in this repo.

Read those when you're doing the work. Read this when you need to understand or explain
*why* the work is structured this way.

---

# Part 1 — Why This Exists

Search used to mean one thing: rank a page in a list of ten blue links, earn a click, let
the page do the rest. That model still matters — but it is no longer the only, or even
the primary, way a lot of people find answers. ChatGPT, Perplexity, Gemini, Copilot, and
Google's own AI Overviews and AI Mode now answer questions directly, synthesizing a
response from a handful of sources and, increasingly, citing them.

That changes the unit of competition. It's no longer "does my page outrank theirs" — it's
"does my page get pulled into the answer at all." A page can rank #1 organically and still
never be cited by an AI system, if the AI can't tell that the content is trustworthy,
can't extract a clean quotable claim from it, or simply doesn't parse its structure
cleanly. Conversely, a page ranking #6 can get cited constantly if it's built the right
way.

Small Factory 5's whole practice — "Built to be cited" — is organized around that shift.
**GEO (Generative Engine Optimization)** is the discipline of making content citable by
AI systems, the same way SEO is the discipline of making it rankable by search engines.
The two aren't in conflict. Traditional rank-and-traffic still gets tracked (step 8) and
still matters — GEO sits alongside it, not instead of it.

Two structures make this repeatable instead of ad hoc:

1. **The Five-Lever Framework** — the *standard*. Every page, in any client's site, in any
   industry, gets evaluated against the same five dimensions of "would an AI cite this."
   It's the yardstick.
2. **The Nine-Step Workflow** — the *process*. The repeatable sequence that takes an
   engagement from "we know nothing about this site yet" to "we're actively tracking and
   protecting citations, and refreshing content before it decays." It's the operating
   system the yardstick runs inside.

Everything below explains both in depth.

---

# Part 2 — The Five-Lever Framework

## What a "lever" is, and why five

An AI system building an answer is doing something specific: pulling a handful of
plausible source documents, extracting whatever's most extractable and trustworthy from
each, and stitching a response. Every one of the five levers corresponds to a specific
point of failure in that pipeline — a specific reason a page that *exists*, and might even
*rank*, still doesn't make it into the answer.

- **Citability** fails when the content exists but there's nothing clean enough to lift.
- **Conversational Alignment** fails when the content answers a question, just not the
  question that's actually being asked, in the phrasing it's actually asked in.
- **Authority Signals** fail when the AI has no way to judge whether the source can be
  trusted, so it reaches for a competitor with clearer signals instead.
- **Factual Density** fails when there's nothing concrete enough to extract — it's all
  tone, no substance.
- **Structured Clarity** fails when the content is fine but the *machine can't parse it*
  correctly, so it never gets chunked and indexed the way it needs to be to surface.

A page can fail on one lever and still get cited sometimes — pass/fail per lever isn't a
single go/no-go gate, it's a diagnostic. But a page that's weak across three or more
levers is a page that's essentially invisible to AI systems regardless of how it performs
organically. The five-lever scorecard on every page review exists to make that visible and
fixable, lever by lever, rather than as a vague "make it more AI-friendly" instruction
nobody can act on.

Every full page review scores all five, as Pass / Needs Work / Fail, with a one-line
reason per lever (see `reports/page-review-template.md` for the exact format).

---

## Lever 1 — Citability

**Core question:** If an AI were writing an answer right now, would it want to lift a
sentence from this page — verbatim or near-verbatim — as the actual answer text?

**Why it matters specifically for AI (not just SEO):** A search engine ranking algorithm
rewards a page for being relevant and authoritative as a *whole document* — it links to
the page and lets the human read it. An AI answer engine does something more surgical: it
extracts a specific span of text, often a sentence or two, and either quotes it directly
or paraphrases it tightly. If a page never contains a self-contained, standalone claim,
there's nothing for the AI to extract — even if the page is relevant and well-ranked, the
AI moves on to a competitor's page that phrased the same fact more cleanly.

**What "clean and quotable" actually looks like:**
- The claim is true and specific without needing the surrounding paragraph for context.
  ("We respond to support tickets within 2 hours, 7 days a week" stands alone. "We're
  known for fast, reliable support" does not — it needs three more sentences of
  justification before it means anything.)
- It reads naturally as a spoken answer. AI-generated responses are voiced as direct
  statements; a claim written as marketing copy ("industry-leading turnaround times")
  doesn't translate into an answer sentence the way a fact does.
- It's positioned where an extraction pass would actually find it — near the top of a
  section, not buried in the fourth paragraph after three sentences of throat-clearing.

**Common failure patterns:**
- **Hedge-everything language.** "We generally try to offer competitive pricing where
  possible" gives an AI nothing firm enough to state as fact.
- **Claims that require the whole page to parse.** A number or fact that only makes sense
  in light of a chart, disclaimer, or paragraph three sections earlier can't be lifted in
  isolation.
- **Marketing fluff with no extractable fact underneath it.** Superlatives ("world-class,"
  "cutting-edge") aren't facts — there's nothing to quote.

**Fix pattern:** Take every vague claim and rewrite it as a specific, checkable one. "We
offer great service" → "We respond to support tickets within 2 hours, 7 days a week."
"Our platform is highly scalable" → "The platform has handled traffic spikes up to 40,000
concurrent users without a service degradation." The rewrite doesn't have to be dramatic —
it has to be *specific enough to stand on its own outside the paragraph it lives in.*

**How this interacts with other levers:** Citability and Factual Density are closely
linked — a citable claim is almost always also a factually dense one — but they're scored
separately because a page can be dense with numbers that are still buried in dense,
unquotable prose (fails Citability, passes Factual Density), or have one clean quotable
sentence sitting in an otherwise vague page (passes Citability narrowly, fails Factual
Density overall).

---

## Lever 2 — Conversational Alignment

**Core question:** Does this page match how a real person actually phrases the question
to an AI assistant — not how an SEO practitioner would phrase a keyword?

**Why it matters specifically for AI:** Keyword-era SEO optimized for query fragments:
"best running shoes," "running shoes waterproof." People don't talk to ChatGPT or
Perplexity that way — they ask full questions, with context: "what running shoes should I
get for wet trail runs in the winter." An AI system trying to match a query to a source is
doing semantic matching against natural language, not fragment matching against a keyword
field. A page built entirely around keyword fragments, with no natural-language framing,
is optimized for a query pattern that's disappearing.

**What to check:**
- **Headers phrased as the actual question.** "How much does implementation cost?" beats
  "Implementation Pricing" as an H2 — not because it's prettier, but because it's a closer
  semantic match to how the question actually gets asked.
- **Answer-first structure.** Lead with the direct answer in the first sentence or two of
  a section, then elaborate. AI extraction favors the front of a section; burying the
  actual answer under two paragraphs of setup means the extraction pass may grab the setup
  instead of the answer.
- **Anticipating the natural follow-up.** A real conversation doesn't stop at one question
  — "what does it cost" is immediately followed by "is there a contract" or "what's
  included." A page that answers the follow-ups too, without making the reader hunt for
  them, mirrors how the AI conversation actually continues.

**Where the actual phrasing comes from:** Don't guess at how people phrase questions —
pull the real phrasing from sales call transcripts, support ticket subject lines, and (per
`prompts/ai-demand-briefs.md`) the literal prompts real users send to AI assistants for
that topic, sourced from AI-visibility tooling. Paraphrasing the "SEO version" of a
question into something that merely sounds conversational is a weaker fix than using the
actual words prospects use.

**Common failure patterns:**
- Headers written as noun phrases ("Pricing," "Features," "Integrations") instead of
  questions, even where a question would be more natural and more specific.
- The answer is technically on the page, but it's the fourth paragraph in, after company
  history and a value-proposition paragraph that has to be read first.
- The page answers the question as phrased in 2015 SEO terms, not as a person (or an AI
  relaying a person's question) would ask it today.

**Fix pattern:** Take the top 3-5 questions a prospect actually asks in sales calls or
support interactions and make sure the page answers each of them directly, near the top of
its own section — not folded into a paragraph about something else.

---

## Lever 3 — Authority Signals

**Core question:** What tells an AI — or a skeptical human reader — that this source is
trustworthy enough to cite, as opposed to just present?

**Why it matters specifically for AI:** An AI system citing a source is making an implicit
trust claim on behalf of the user reading its answer. That means AI systems (like careful
human readers) look for the same signals search engines have long rewarded under E-E-A-T
(Experience, Expertise, Authoritativeness, Trustworthiness) — but arguably weight them more
heavily, because there's no human in the loop double-checking the source before the
information gets relayed as fact. A page with a correct answer and zero authority signals
is a bigger citation risk for the AI than a page with a slightly less polished answer but
clear, verifiable expertise behind it.

**What to check:**
- **Author/entity attribution.** Is it clear who wrote this, or what organization stands
  behind the claim? Anonymous, unattributed content is a weak citation candidate almost
  regardless of how good the content itself is.
- **Credentials and specificity of expertise.** Years of experience, certifications, named
  specializations — not just "our team of experts," but *whose* expertise, in what,
  demonstrated how.
- **External validation.** Reviews, case studies, press mentions, named client logos —
  third-party signals the AI (and the reader) doesn't have to just take the page's word
  for.
- **Sourcing behind claims.** Are assertions backed by data, a named study, or a concrete
  example — or is it assertion stacked on assertion with nothing underneath?

**Common failure patterns:**
- A strong, well-written page with no byline, no author bio, no indication of who or what
  organization is making the claims.
- "We're the industry leader in X" with no named ranking, study, client count, or metric
  behind it — an unsupported superlative reads as a red flag, not a credibility signal.
- Real credentials that exist but live on a separate About page, disconnected from the
  content making the claims that those credentials would actually support.

**Fix pattern:** Add a byline and short bio linking to real credentials. Replace an
unsupported superlative with a real number, named case study, or specific credential.
Where third-party validation exists (reviews, press, client logos) but isn't surfaced on
the page itself, bring it onto the page rather than leaving it siloed elsewhere on the
site.

---

## Lever 4 — Factual Density

**Core question:** Is this page full of specific, checkable information, or is it mostly
tone and adjectives standing in for substance?

**Why it matters specifically for AI:** Factual density is the raw material Citability and
Authority Signals are built from — a page can't produce a clean quotable claim (Lever 1)
or back an assertion with real sourcing (Lever 3) if there's no actual fact underneath the
sentence to begin with. This lever asks the more basic question first: is there *anything*
concrete here at all?

**What to check:**
- **The ratio of concrete nouns/numbers/names to vague adjectives.** "Industry-leading,"
  "best-in-class," "world-class," "cutting-edge" are tells that a sentence is doing
  persuasion work instead of information work.
- **Dates, figures, named products/models/versions** where the topic calls for them —
  precision is a citability signal in itself.
- **Repetition disguised as elaboration.** Restating the same unsupported claim in three
  different sentences with different adjectives isn't adding density, it's padding —
  and it's also a known pattern AI systems are increasingly good at discounting as
  low-information filler.

**Common failure patterns:**
- A paragraph that, read closely, contains zero facts a reader couldn't have guessed
  before reading it — pure tone.
- Numbers that exist but are stale, rounded to the point of meaninglessness, or missing
  the context that would make them checkable (a percentage with no baseline, a "since
  [year]" with no explanation of why that year matters).
- Long-form content that's long because it repeats itself, not because it covers more
  ground.

**Fix pattern:** For every vague superlative, either replace it with a real, specific
number or named fact, or cut it outright. If a claim can't be made specific because the
underlying fact genuinely doesn't exist yet (no case study, no measured number), that's a
flag for the client to go get the data, not a cue to paper over the gap with stronger
adjectives.

---

## Lever 5 — Structured Clarity

**Core question:** Could a machine parse this page's structure correctly, without having
to guess at what belongs to what?

**Why it matters specifically for AI:** Before an AI system can decide whether a page is
citable, authoritative, or dense, it has to correctly parse the page into meaningful
chunks. A logically messy page — skipped heading levels, no schema, several unrelated
topics crammed under one H1 — makes that parsing step unreliable, which means even
genuinely strong content underneath can get mis-chunked, under-extracted, or missed
entirely. This is the lever that determines whether the other four levers' work even gets
*seen* correctly.

**What to check:**
- **Logical heading hierarchy.** H1 → H2 → H3 in order, no skipped levels, no using
  heading tags for visual styling rather than actual structure.
- **Schema markup where applicable.** Organization, Product, FAQ, Article, and other
  structured-data types give an AI system (and a search engine) an explicit, unambiguous
  signal about what kind of content this is and how its pieces relate — rather than making
  it infer that from prose alone.
- **Scannable formatting.** Lists, tables, and short paragraphs parse more reliably than
  dense unbroken blocks of text — both for machines and for the human skimming an answer.
- **One clear topic per page.** A page trying to cover several competing subjects at once
  is harder for both a search engine and an AI system to classify and chunk correctly than
  several focused pages linked together.

**Common failure patterns:**
- Heading levels chosen for font size rather than document structure (an H4 used because
  it "looks right" visually, breaking the logical H1→H2→H3 chain).
- FAQ-style content sitting on the page as plain paragraphs with no `FAQPage` schema
  connecting the questions to their answers explicitly.
- A single page trying to be both a product page and a comparison guide and a pricing
  page, with no clear primary topic a machine (or a human) could name in one sentence.

**Fix pattern:** Break up dense paragraphs into scannable lists/short paragraphs. Fix
heading-hierarchy gaps so the document outline actually reflects the content's logical
structure. Add FAQ schema to existing Q&A-shaped content rather than leaving that
relationship implicit. Where a page covers multiple competing topics, split it and link
the resulting pages together clearly (which is also Step 3's job at the site level, not
just the page level).

---

## How the five levers interact

They aren't five independent checkboxes — they reinforce and gate each other:

- **Structured Clarity is a prerequisite**, in a sense, for the other four to even be
  correctly evaluated by a machine — a strong claim inside a badly-structured page may
  never get parsed cleanly enough to be recognized as citable at all.
- **Factual Density feeds Citability** — a citable claim is built from dense, specific
  facts; density without a clean, standalone sentence to carry it doesn't help.
- **Authority Signals raise the trust ceiling** on everything else — the same fact, cited
  from an anonymous unattributed page versus a page with clear author credentials and
  sourcing, is treated differently by both AI systems and skeptical human readers.
- **Conversational Alignment determines whether the right query ever reaches the page** —
  a page can pass every other lever and still never surface if it's never semantically
  matched to how the question is actually asked.

A page that's weak on one lever with everything else strong is usually a quick, high-value
fix. A page weak across three or more is a sign the page needs to be substantially
rewritten, not lightly edited — that distinction is what the self-serve vs. dev/IT and
"what I'd prioritize first" sections of every page review are for.

---

# Part 3 — The Nine-Step Workflow

Five phases, nine steps, in a fixed order — Audit, Structure, Create, Measure, Repeat.
Every engagement runs through this same sequence; a single page-review engagement just
stops earlier (effectively Step 5 alone, with Steps 1-2 done informally by reading the
page and the client-facts rather than running a full site crawl).

## Phase overview

| Phase | Steps | What it establishes |
|---|---|---|
| **Audit** | 1 (1A/1B)-2 | The baseline — what exists, and what AI systems currently say |
| **Structure** | 3-4 | The foundation — how pages connect, what markup is missing |
| **Create** | 5-6 | The actual work — every page optimized, every gap identified |
| **Measure** | 7-8 | Proof — is citation and traffic actually moving |
| **Repeat** | 9 | Durability — catching decay before it costs citations |

---

## Step 1A — AI Visibility Grader Snapshot
*Phase: Audit*

**Why this is first:** Before any repo tooling gets involved, a single-input pass through an
external AI-visibility grader gives an immediate, zero-setup read on where the client
currently stands. It's lighter than Step 2's full citation-gap analysis, but it's fast
enough to run in the first five minutes of an engagement and gives something concrete to
anchor the deeper Step 2 analysis against once that runs.

**Detailed process:**
1. Go to [ai.grader.searchinfluence.com](https://ai.grader.searchinfluence.com).
2. Enter the client's web address.
3. Save the resulting score/grade/summary (a screenshot is fine) into
   `clients/<client>/data/ai-visibility/`.

**Deliverable:** A single grader snapshot on file — no repo tooling involved, this is a
manual external-tool check, not an automated pull.

**Cadence:** Once, at engagement kickoff, before Step 1B.

---

## Step 1B — Full-Site Crawl & Technical Baseline
*Phase: Audit*

**Why this comes next:** Every later step depends on knowing what's actually on the site.
Content quality can't be judged, a linking map can't be built, and a citation gap can't be
measured against a baseline that doesn't exist yet. Skipping this step means every later
recommendation is built on assumptions instead of a real inventory.

**Detailed process:**
1. Run a full crawl of the client's domain (Screaming Frog is the default tool; a paid
   license is required past 500 URLs).
2. Export the **Internal All** report — every internal URL with its status code,
   indexability, title, meta description, H1, word count, and canonical target.
3. Export the **All Inlinks** report — the internal link graph, source → destination for
   every internal link on the site. This doubles as Step 3's primary input.
4. Build the indexation summary: total pages, indexable vs. non-indexable, and the
   specific reason for each non-indexable page (404, canonicalized elsewhere, noindex,
   redirect chain).
5. Flag every non-200 status code — these block everything downstream and get fixed
   first, ahead of any content work.
6. Cross-reference titles, meta descriptions, and H1s across the whole site for
   duplicates — a duplicate signal often means two pages are unintentionally competing for
   the same topic.
7. Flag thin content — indexable pages below a reasonable word-count floor for their
   content type (roughly 300 words as a default, adjusted per the client's content norms).
8. Cross-reference the page inventory against the inlink graph to flag orphan pages —
   indexable URLs with zero internal inlinks pointing to them.

**Deliverable:** A technical baseline report — page counts, indexation breakdown,
prioritized error list, duplicate/thin/orphan flags. This is a findings document only;
fixes get scoped later once Step 5 reviews the actual page content.

**Cadence:** Once, at engagement start. Re-run after any major structural change
(replatform, large content purge, site migration) — a six-month-old crawl is not a current
baseline.

---

## Step 2 — AI Citation Gap Analysis
*Phase: Audit*

**Why this matters:** Before recommending any change aimed at improving AI visibility, you
need to know the actual starting point — what, if anything, AI assistants currently say
about this client, and who they cite instead on the client's own core topics. Without this
baseline, "did GEO work improve citations" is a guess, not a measurement (this is exactly
what Step 7 later compares against). This is a deeper, multi-source analysis than Step 1A's
grader snapshot — Step 1A is a fast single-tool check at kickoff, Step 2 is the full
baseline everything else gets measured against.

**Detailed process:**
1. Pull an AI-visibility export (Semrush AI Visibility, Scrunch, or another monitoring
   tool) covering the client's brand terms and core topics.
2. Cross-reference against Search Console data for the same queries/topics.
3. Bucket every query/topic into three groups:
   - **Earned-but-uncited** — ranking well organically (position ≤ 5) but never cited by
     any AI engine. This is a strong signal the content exists and ranks, but fails one or
     more of the five levers badly enough that AI systems pass over it.
   - **Cited-but-weak-page** — an AI engine is citing the client, but not from their
     strongest page on the topic — often a sign of cannibalization (multiple pages
     competing, the AI picked the wrong one) worth flagging for Step 3.
   - **Winners to protect** — queries where the client both ranks and gets cited. Note
     these explicitly so later work doesn't inadvertently disturb something that's already
     working.
4. Where more than one AI-visibility tool is available, triangulate — different tools
   have different engine coverage (Semrush skews Gemini/Google AI surfaces; Scrunch adds
   Perplexity and Copilot coverage). Treat agreement between tools as higher-confidence,
   disagreement as a coverage difference to investigate rather than a contradiction to
   report as fact.
5. Treat every AI-visibility number as directional, not precise — single-run citation
   counts vary between runs of the same query. The value is the pattern across many
   queries, not any individual number.

**Deliverable:** The engagement's AI-visibility baseline report, in the three buckets
above, every claim sourced to its specific file and engine.

**Cadence:** Once, at engagement start — this is the reference point Step 7 tracks change
against for the life of the engagement.

---

## Step 3 — Information Architecture & Internal Linking Map
*Phase: Structure*

**Why this matters:** A page can pass every one of the five levers on its own merits and
still underperform if it sits in isolation, disconnected from the rest of the site's
topical structure. Both search engines and AI systems read internal linking patterns as a
signal of what a site considers important and how topics relate to each other — an orphan
page, however well-written, reads as low-priority almost by definition.

**Detailed process:**
1. Start from Step 1B's orphan and thin-link flags — don't re-derive them, extend them.
2. Cluster the site's pages by topic, using URL path structure and title/H1 similarity as
   the signal (there's no automated topic-clustering tool here — this is a careful manual
   read of the crawl export, not a guess from URLs alone).
3. Name each cluster and identify, within each one, any duplicate or directly competing
   pages flagged back in Step 1B — decide here whether the right fix is consolidation (301
   redirect + merge the content) or differentiation (distinct angles on the same broad
   topic, cross-linked rather than merged).
4. For every orphan or thin-link page, name 2-4 specific existing pages — chosen for
   topical relevance and existing link strength, not just "link everything from the
   homepage" — that should link to it, along with the anchor text to use.
5. Where a cluster has four or more pages and no page that links out to all of them,
   flag the missing hub/category page — either recommend building one, or promoting the
   cluster's strongest existing page into that role.

**Deliverable:** A linking map: the cluster list, specific link-from → link-to
recommendations with anchor text, and any hub-page gaps. This produces a map only —
implementing the links is a self-serve or dev/IT task depending on the client's CMS.

**Cadence:** Once, early in the engagement. Revisit once Step 6 (content gap fill) has
added enough new pages that the map is stale.

---

## Step 4 — Schema & Structured Data Plan
*Phase: Structure*

**Why this matters:** Schema markup (JSON-LD structured data) is the most direct, explicit
way to tell a search engine or AI system what a piece of content actually is — an
Organization, a Product, an FAQ, an Article — rather than making it infer that from prose
alone. This directly serves Lever 5 (Structured Clarity), but at the site level rather
than the single-page level: it's about identifying *which* structured data types are
missing across the site, not just fixing one page.

**Detailed process:**
1. Identify the content types present across the site that have a corresponding schema
   type — FAQ sections, product listings, articles/blog posts, the organization's own
   identity information.
2. For each, confirm whether schema is present, present-but-incomplete, or entirely
   missing.
3. Write the missing or corrected markup as copy-ready JSON-LD — not a description of what
   schema *should* exist, an actual snippet a developer can drop in directly.
4. Pair every snippet with a short dev ticket note: what it's for, and where in the page
   template it goes.

**Deliverable:** JSON-LD snippets plus dev ticket notes, either embedded directly in each
page's individual review (Step 5) or rolled into one standalone site-wide schema plan.

**Cadence:** Once per page (as part of Step 5), revisited whenever a new page type gets
introduced to the site that doesn't yet have its schema pattern established.

---

## Step 5 — Five-Lever Page Optimization
*Phase: Create*

**Why this is the center of the whole engagement:** This is where Part 2's framework
actually gets applied, page by page. Every other step either feeds this one (Steps 1-4
establish what needs fixing and in what order) or measures its results (Steps 7-9 track
whether it worked). If an engagement only has budget or time for one thing, this is it.

**Detailed process:**
1. Confirm which client this is for — never assume; ask if it isn't already stated.
2. Read that client's `client-facts.md` in full before touching the page — brand voice,
   off-limits claims, known corrections, competitors.
3. Pull the actual page content — fetch the live URL, or use the provided file/paste
   directly. Never review a page that wasn't actually read.
4. Score all five levers — Citability, Conversational Alignment, Authority Signals,
   Factual Density, Structured Clarity — each as Pass / Needs Work / Fail with a one-line
   reason, per the detailed criteria in Part 2.
5. Cross-check every claim on the page against `client-facts.md` — flag anything that
   contradicts a known fact, violates an off-limits claim, or breaks the client's brand
   voice guidance.
6. Write prioritized fixes in two explicit lists: **self-serve** (copy/content changes
   anyone can make directly) and **dev/IT required** (schema, technical structure,
   anything needing a developer) — never blended together.
7. Draft the actual rewritten elements where relevant: title tag, meta description, H1,
   an answer-first opening paragraph, an FAQ block if the topic calls for one.
8. Where schema is needed, write it as copy-ready JSON-LD plus a short dev ticket (this is
   Step 4 applied at the individual-page level).
9. Fill the standard report template with all of the above, in Small Factory 5's brand
   voice.
10. Save the finished report to the client's dated reports folder.

**Deliverable:** The core client deliverable — a five-lever scorecard, prioritized
self-serve and dev/IT fixes, and rewritten on-page elements, in the standard report
format.

**Cadence:** Per page, throughout the engagement — this is the workflow that runs whenever
the request is "review/audit/score this page," for any client, at any point.

---

## Step 6 — Content Gap Fill
*Phase: Create*

**Why this matters:** Step 5 fixes what exists. This step finds what's missing entirely —
topics competitors get cited on that the client doesn't cover at all. A perfectly-executed
five-lever review of an existing page can't fix a gap where no page exists yet; that
requires identifying the gap and building new content, not editing.

**Detailed process:**
1. Pull AI-demand data — topic volume and the literal prompts real users send to AI
   assistants on those topics (from the same AI-visibility tooling used in Step 2).
2. Cross-reference against Search Console to distinguish validated demand (topics with
   real organic impressions already) from AI-only directional demand.
3. Rank the gaps by size — high AI/topic demand, low or no current coverage — and drop
   anything that doesn't fit the client's actual priority topics.
4. For each opportunity in scope, pull the literal phrasing of the real questions people
   ask — these become the page's FAQ entries, H2s, and overall angle. Use the real
   phrasing, not a paraphrase (this directly serves Lever 2, Conversational Alignment,
   from the moment the page is drafted rather than fixed after the fact).
5. Look at which existing (often competitor) pages are actually getting cited for that
   topic, and note the shape of their content — answer-first, list format, comparison
   table — so the new brief is built in a citable shape from the start.
6. Output a prioritized brief per opportunity: target topic, the demand signal and which
   sources confirm it, the literal questions to answer, recommended internal-link siblings
   (tying back to Step 3's cluster map), the recommended format, and whether this should be
   a new page or a meaningful refresh of something that already exists.

**Deliverable:** A prioritized content brief list, ready to hand to a writer or use
directly as a content roadmap.

**Cadence:** Once per engagement start, then on an ongoing basis whenever Step 7's
tracking surfaces a new demand signal worth acting on.

---

## Step 7 — AI Share-of-Voice Tracking
*Phase: Measure*

**Why this matters:** Without ongoing measurement, "is the GEO work paying off" is a
feeling, not a fact. This step turns Step 2's one-time baseline into a recurring trend
line, so a client (and Small Factory 5) can see whether citation frequency is actually
moving, not just assume it is because the reports look thorough.

**Detailed process:**
1. Pull a fresh AI-visibility export on the same recurring cadence as the engagement's
   reporting schedule (monthly is the default for a retainer).
2. Re-run the same triangulation process as Step 2 — confirmed wins where multiple tools
   agree, disagreements to flag as engine-coverage differences rather than contradictions,
   and gaps where one tool sees an engine the other doesn't.
3. Diff the current bucketed results against the Step 2 baseline (or the prior period's
   results, once more than one cycle has run) to show actual movement, not just a
   snapshot.
4. Flag anything that moved the wrong direction — a previously-cited page that's dropped
   out — with the same urgency as flagging a win, since decay (Step 9) can show up here
   first, before a page review would otherwise catch it.

**Deliverable:** A dated trend report — confirmed wins, disagreements under
investigation, engine-coverage gaps, framed against the established baseline.

**Cadence:** Recurring, on the retainer's reporting cadence (monthly by default — confirm
the specific cadence in the client's contract).

---

## Step 8 — Rank & Traffic Monitoring
*Phase: Measure*

**Why this matters:** GEO doesn't replace traditional search performance — it sits
alongside it. A client (correctly) still cares whether organic rankings and traffic are
healthy, and some of the highest-value opportunities only show up when rank/traffic data
is cross-referenced against paid spend or AI-citation data, not viewed in isolation.

**Detailed process:**
1. Pull current Search Console and GA4 (or equivalent analytics) data for the reporting
   period.
2. Run the high-impression/low-CTR analysis — queries earning visibility but losing the
   click, usually a title/meta or intent-match problem — and pair each with the
   landing page's engagement/conversion data to judge whether fixing it is actually worth
   prioritizing.
3. Run the paid-organic overlap analysis — queries where the client both ranks well
   organically and is paying for the same term — surfacing dollars that could potentially
   be reallocated away from redundant paid spend, and separately flagging terms that are
   worth keeping paid despite already ranking (high strategic value, or high CPA without
   organic strength elsewhere).
4. Lead every recommendation with the number, sourced to its file and date range — never
   an unsourced directional claim.

**Deliverable:** Prioritized opportunity lists — high-impression/low-CTR fixes, paid-spend
reallocation candidates — dated to the reporting period.

**Cadence:** Recurring, the same cadence as Step 7 — the two are normally reported
together as one combined measurement update.

---

## Step 9 — Content Decay Refresh & Reporting
*Phase: Repeat*

**Why this matters:** Content that was accurate and well-optimized a year ago doesn't stay
that way on its own. Prices change, products get discontinued, competitors publish
stronger pages on the same topic, and facts quietly go stale. Left unchecked, decay costs
citations gradually and invisibly — by the time a client notices citations have dropped,
the underlying cause may have been sitting there for months. This step exists to catch
that proactively instead of reactively.

**Detailed process:**
1. Identify the batch in scope — pages last reviewed more than one reporting cycle ago
   (90+ days on a quarterly cadence), or the full set of previously-reviewed pages if this
   is the client's first decay pass.
2. Re-pull each page's *current* live content — never reuse the old review's cached text,
   since the whole point is catching what's changed.
3. Re-run the full five-lever scorecard on the current content and diff it against the
   prior review's scores — call out any lever that's regressed, and why (a stat that's
   gone stale is a Factual Density regression; a since-removed author bio is an Authority
   Signals regression, etc.).
4. Check every on-page claim against `client-facts.md`, specifically its correction log —
   this is where "the client discontinued X" or "the price changed to Y" facts live, and
   is the fastest way to catch a claim that's now flatly wrong.
5. Check competitive standing — has a competitor published something more thorough on this
   topic since the last review — and pair with a quick re-check of the page's current
   AI-citation status.
6. Write refresh recommendations in the same self-serve/dev-IT split as a standard page
   review — this is a full review re-run, not just a flag that something's old.
7. Roll the whole batch into one recurring report rather than a report per page (unless a
   single page needs isolated, urgent attention) — this is meant to read as a periodic
   health check.

**Deliverable:** A dated decay report per batch: which pages were checked, what changed
since the last review, and prioritized refresh actions — cleared through the
pre-delivery checklist before it goes external.

**Cadence:** Recurring, less frequently than Steps 7-8 — quarterly is the reasonable
default, confirmed against the specific retainer's scope. A page that's never been
reviewed before isn't a decay case — it routes to Step 5 as a first review instead.

---

# Part 4 — How the Whole Thing Fits Together

A full retainer engagement runs the nine steps roughly on this timeline:

- **Weeks 1-2:** Steps 1A-2 (grader snapshot + crawl + AI-citation baseline) establish where
  things stand.
- **Weeks 2-4:** Steps 3-4 (linking map + schema plan) fix the structural foundation
  before content work starts, so Step 5's page-level fixes aren't undone by a broken site
  architecture underneath them.
- **Ongoing through the engagement:** Steps 5-6 (page optimization + content gap fill) are
  the continuous work — every existing page gets reviewed and fixed, every real content
  gap gets briefed and built.
- **Every reporting cycle (monthly by default):** Steps 7-8 (AI share-of-voice + rank and
  traffic) prove the work is moving the numbers, in both the AI-citation and traditional
  search sense.
- **Every quarter (by default):** Step 9 (decay refresh) protects everything already built
  from quietly going stale.

A one-off, single-page engagement is effectively Step 5 in isolation, with Steps 1-2 done
informally — reading the page and the client-facts carefully, rather than running a full
site crawl and AI-visibility export first.

The two structures — the five levers and the nine steps — aren't separate systems
running in parallel. The levers are the standard the nine-step process exists to apply,
protect, and re-apply as content and competitive landscapes change. Step 5 is where they
meet directly; every other step exists to make sure Step 5's work is built on an accurate
baseline (Steps 1-2), a sound structural foundation (Steps 3-4), complete coverage
(Step 6), and durable results (Steps 7-9).
