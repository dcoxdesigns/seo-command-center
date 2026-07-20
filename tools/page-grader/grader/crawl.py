"""Internal-linking recommendations from a Screaming Frog crawl export —
implements the methodology from the on-page review process this tool was
compared against (inbound candidate scoring by keyword overlap, outbound
opportunities by finding real anchor phrases already in the page's own
copy — never inventing anchor text).

Deterministic, not AI-judged: candidate/gap detection is a real computation
on real crawl data, not a subjective call, so it's its own report section
rather than folded into the AI-scored SEO Intent Match table.

Opt-in per client: if clients/<slug>/data/crawl/internal_all.csv (and
optionally all_inlinks.csv) doesn't exist, this silently returns no
recommendations — no crawl, no linking section, no error. Matches the
"Screaming Frog license needed for 500+ URLs, free tier fine below that"
note already in prompts/site-crawl-baseline.md.

Column names match Screaming Frog's real export headers exactly (see
data/crawl/sample-internal-all.csv / sample-all-inlinks.csv) — this reads
those columns, it doesn't assume a generic schema.
"""

import csv
import os
import re
from collections import Counter
from urllib.parse import urlparse

STOPWORDS = {
    "a", "an", "the", "and", "or", "for", "to", "of", "in", "on", "is", "are",
    "with", "your", "you", "we", "our", "how", "what", "why", "at", "by", "it",
}

# A term appearing in this fraction (or more) of all page titles/H1s carries no
# topical signal — computed dynamically from the actual crawl, not a fixed list,
# per the reference process's definition of boilerplate. Also requires this many
# *absolute* pages, not just the ratio — on a small crawl (a handful of pages,
# e.g. early in a Site Audit or a niche site), a genuinely topical term can
# appear on 2-3 pages and still cross a 50% ratio; the absolute floor keeps
# small crawls from misclassifying real signal as boilerplate.
BOILERPLATE_THRESHOLD = 0.5
BOILERPLATE_MIN_PAGES = 8


def _normalize(word):
    # Crude suffix stripping so "tent"/"tents" or "box"/"boxes" overlap —
    # no real stemmer here (no dependency for it), just enough to catch
    # plain plurals without mangling short words or words already ending "ss".
    if len(word) > 4 and word.endswith("es") and not word.endswith("ses"):
        return word[:-2]
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def _tokenize(text):
    words = re.findall(r"[a-z0-9]+", (text or "").lower())
    return [_normalize(w) for w in words if w not in STOPWORDS and len(w) > 2]


def _slug_tokens(url):
    path = urlparse(url).path
    return _tokenize(re.sub(r"[/_-]+", " ", path))


def load_crawl(client_slug, clients_dir):
    """Returns {"pages": [...], "inlinks": [...] or None} or None if no crawl
    export exists for this client. pages/inlinks are lists of dict rows keyed
    by the exact Screaming Frog column names."""
    crawl_dir = os.path.join(clients_dir, client_slug, "data", "crawl")
    internal_path = os.path.join(crawl_dir, "internal_all.csv")
    if not os.path.exists(internal_path):
        return None

    with open(internal_path, newline="", encoding="utf-8-sig") as f:
        pages = list(csv.DictReader(f))

    inlinks_path = os.path.join(crawl_dir, "all_inlinks.csv")
    inlinks = None
    if os.path.exists(inlinks_path):
        with open(inlinks_path, newline="", encoding="utf-8-sig") as f:
            inlinks = list(csv.DictReader(f))

    return {"pages": pages, "inlinks": inlinks}


def _is_indexable(page):
    return (page.get("Indexability") or "").strip().lower() == "indexable"


def _boilerplate_terms(pages):
    doc_count = Counter()
    total = 0
    for page in pages:
        if not _is_indexable(page):
            continue
        total += 1
        terms = set(_tokenize(page.get("Title 1", "")) + _tokenize(page.get("H1-1", "")))
        for t in terms:
            doc_count[t] += 1
    if total == 0:
        return set()
    return {
        t for t, c in doc_count.items()
        if c / total >= BOILERPLATE_THRESHOLD and c >= min(BOILERPLATE_MIN_PAGES, total)
    }


def _existing_inbound_sources(inlinks, target_url):
    if inlinks is None:
        return None  # unknown — can't confirm vs. candidate without edge-level data
    return {row.get("Source") for row in inlinks if row.get("Destination") == target_url}


def find_inbound_candidates(crawl, target_url, limit=5):
    """Other pages that topically overlap with target_url and could link to it.
    Labeled "confirmed gap" if all_inlinks.csv shows they don't already link
    there, "candidate to spot-check" if inlinks data wasn't available to check —
    matches the reference process's own caution about what a page-summary crawl
    export can and can't confirm."""
    pages = crawl["pages"]
    target = next((p for p in pages if p.get("Address") == target_url), None)
    if target is None:
        return []

    boilerplate = _boilerplate_terms(pages)
    target_terms = Counter(
        t for t in (_tokenize(target.get("Title 1", "")) + _tokenize(target.get("H1-1", "")) + _slug_tokens(target_url))
        if t not in boilerplate
    )
    if not target_terms:
        return []

    already_linking = _existing_inbound_sources(crawl["inlinks"], target_url)
    confirmed = already_linking is not None

    scored = []
    for page in pages:
        url = page.get("Address")
        if url == target_url or not _is_indexable(page):
            continue
        if confirmed and url in already_linking:
            continue
        candidate_terms = set(
            t for t in (_tokenize(page.get("Title 1", "")) + _tokenize(page.get("H1-1", "")))
            if t not in boilerplate
        )
        overlap = candidate_terms & set(target_terms)
        if not overlap:
            continue
        # Rare shared terms (fewer target_terms sharing them elsewhere) count more —
        # simple proxy: sum of 1/frequency-in-target isn't meaningful with one target,
        # so weight by how many distinct overlapping terms, tie-broken by page word count.
        score = len(overlap)
        scored.append((score, page, sorted(overlap)))

    scored.sort(key=lambda x: (-x[0], -_safe_int(x[1].get("Word Count"))))
    status = "confirmed gap" if confirmed else "candidate to spot-check"
    return [
        {
            "url": page.get("Address"),
            "title": page.get("Title 1"),
            "shared_terms": terms,
            "status": status,
        }
        for _, page, terms in scored[:limit]
    ]


def _safe_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def find_outbound_opportunities(page_text, crawl, own_url, limit=8):
    """Other pages whose title or H1 appears as a real phrase already in this
    page's own visible text — the anchor text is found, not invented. Skips
    pages whose title is too short/generic to match meaningfully."""
    if not page_text:
        return []
    haystack = page_text.lower()
    pages = crawl["pages"]
    boilerplate = _boilerplate_terms(pages)

    found = []
    for page in pages:
        url = page.get("Address")
        if url == own_url or not _is_indexable(page):
            continue
        for field in ("Title 1", "H1-1"):
            phrase = (page.get(field) or "").strip()
            if len(phrase) < 8:
                continue
            phrase_terms = set(_tokenize(phrase)) - boilerplate
            if len(phrase_terms) < 2:
                continue  # too generic/short to be a meaningful topical match
            if phrase.lower() in haystack:
                found.append({"anchor_text": phrase, "url": url, "title": page.get("Title 1")})
                break

    return found[:limit]
