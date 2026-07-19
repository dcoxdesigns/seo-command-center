"""Mention/citation detection — does a platform response surface this client?

Mentioned: the domain or any brand variant appears in the response text
(case-insensitive substring match).
Cited: one of the platform's returned citation URLs resolves to the client's
domain (matches the domain itself or any subdomain of it).
"""

import re
from urllib.parse import urlparse


def _normalize_domain(domain):
    domain = domain.strip().lower()
    domain = re.sub(r"^https?://", "", domain)
    domain = domain.split("/")[0]
    domain = domain[4:] if domain.startswith("www.") else domain
    return domain


def is_mentioned(response_text, domain, brand_variants):
    if not response_text:
        return False
    text = response_text.lower()
    needles = [_normalize_domain(domain)] + [v.strip().lower() for v in brand_variants if v.strip()]
    return any(needle in text for needle in needles if needle)


def _url_matches_domain(url, domain):
    try:
        netloc = urlparse(url).netloc.lower()
    except ValueError:
        return False
    netloc = netloc[4:] if netloc.startswith("www.") else netloc
    return netloc == domain or netloc.endswith("." + domain)


def cited_urls(citation_urls, domain):
    """Returns the subset of citation_urls that actually resolve to the client's domain."""
    target = _normalize_domain(domain)
    return [u for u in (citation_urls or []) if _url_matches_domain(u, target)]


def is_cited(citation_urls, domain):
    return len(cited_urls(citation_urls, domain)) > 0
