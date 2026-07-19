"""Which other domains show up as citation sources across a client's tracked
prompts. Feeds the "Who's Getting Cited Instead" section of the client-facing
report — the same competitive-gap question step 2 of the nine-step process
(AI Citation Gap Analysis) asks manually.
"""

import json
from collections import Counter
from urllib.parse import urlparse

from . import db


def _domain_of(url):
    try:
        netloc = urlparse(url).netloc.lower()
    except ValueError:
        return None
    return netloc[4:] if netloc.startswith("www.") else (netloc or None)


def top_competing_domains(conn, client, timestamp, own_domain, limit=10):
    """Domains other than the client's own that appeared as citations in this
    run, most-frequent first, each with one example prompt they showed up on."""
    rows = db.rows_for_run(conn, client, timestamp)
    own = own_domain.strip().lower()
    own = own[4:] if own.startswith("www.") else own

    counts = Counter()
    examples = {}
    for row in rows:
        for url in json.loads(row["citation_urls"] or "[]"):
            domain = _domain_of(url)
            if not domain or domain == own or domain.endswith("." + own):
                continue
            counts[domain] += 1
            examples.setdefault(domain, row["prompt"])

    return [
        {"domain": domain, "count": count, "example_prompt": examples[domain]}
        for domain, count in counts.most_common(limit)
    ]
