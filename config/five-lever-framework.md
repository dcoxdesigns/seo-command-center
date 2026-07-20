# The Five-Lever Framework

Every page — any client, any industry — gets evaluated against these five levers before
it's considered "done." This is the shared standard referenced by every workflow in this repo.

---

## 1. Citability
**The question:** If an AI were writing an answer, would it want to lift a sentence from
this page verbatim or near-verbatim?

**What to check:**
- Is there at least one clean, self-contained, quotable claim per major section?
- Are claims specific enough to stand alone outside their paragraph's context?
- Avoid: hedge-everything language, marketing fluff with no extractable fact.

**Quick fix pattern:** Rewrite vague claims ("we offer great service") into specific,
citable ones ("we respond to support tickets within 2 hours, 7 days a week").

---

## 2. Conversational Alignment
**The question:** Does this page match how a real person would phrase the question to an
AI assistant — not how an SEO would phrase a keyword?

**What to check:**
- Headers phrased as natural questions where appropriate ("How much does X cost?" not
  just "Pricing").
- Answer-first structure: lead with the direct answer, then elaborate.
- Does the page anticipate follow-up questions a curious reader/AI would have next?

**Quick fix pattern:** Take the top 3-5 questions a prospect actually asks in sales calls
or support tickets and make sure the page answers them directly, near the top.

---

## 3. Authority Signals
**The question:** What tells an AI (or a skeptical human) this source is trustworthy
enough to cite?

**What to check:**
- Author/entity attribution — is it clear who wrote this or what organization stands
  behind it?
- Credentials, certifications, years of experience, named expertise where relevant.
- External validation: reviews, case studies, press mentions, client logos.
- Sourcing: are claims backed by data, studies, or named examples rather than assertion?

**Quick fix pattern:** Add a byline/bio, link to credentials, or cite a real number/case
study instead of an unsupported superlative.

---

## 4. Factual Density
**The question:** Is this page full of specific, checkable information, or is it mostly
tone and adjectives?

**What to check:**
- Ratio of concrete nouns/numbers/names to vague adjectives ("industry-leading,"
  "best-in-class," "world-class").
- Dates, figures, named products/models/versions where applicable.
- Avoid AI-detectable filler: repetitive restating of the same claim in different words.

**Quick fix pattern:** For every vague superlative, either replace it with a real number
or cut it.

---

## 5. Structured Clarity
**The question:** Could a machine parse this page's structure correctly without guessing?

**What to check:**
- Logical heading hierarchy (H1 → H2 → H3, no skipped levels).
- Schema markup where applicable (Article, Product, FAQ, Organization, etc.).
- Scannable formatting: lists, tables, short paragraphs over dense blocks.
- One clear topic per page — not several competing subjects crammed together.

**Quick fix pattern:** Break up dense paragraphs, add FAQ schema to existing Q&A content,
fix heading hierarchy gaps.

---

## Using this framework
- Every full page review scores all five levers 0-10 (9-10 exceptional, 7-8 Pass, 4-6
  Needs Work, 1-3 Fail, 0 absent) — the number is the source of truth, Pass/Needs
  Work/Fail is a label derived from it, not a separate judgment call. Average the five
  scores and scale to 100 for the page's composite GEO Score, reported alongside (not
  blended into) the SEO Intent Score from `prompts/page-reviewer.md` step 3.
- Self-serve fixes (copy, headers, structure) vs. dev/IT fixes (schema implementation,
  technical markup) get split clearly in any client-facing report.
- This file is shared across all clients. Client-specific tone, examples, and constraints
  live in `clients/<name>/client-facts.md`, not here.