"""Shared interface every platform module implements.

Each platform module exposes:
    NAME: str
    ENV_KEY: str                 — env var holding the API key
    call(prompt: str, api_key: str) -> PlatformResponse

Platform API response shapes are the least stable part of this tool — each
provider's web-search/grounding feature has changed field names before and
will again. If a live run raises here, check the provider's current docs
first; the raw HTTP response is always logged to disk before parsing (see
runner.py), so a bad parse never loses data, only requires a re-parse.
"""

from dataclasses import dataclass, field


@dataclass
class PlatformResponse:
    text: str
    citation_urls: list = field(default_factory=list)
    raw: dict = field(default_factory=dict)
    error: str = None


class PlatformError(Exception):
    """Raised on a request/parse failure. The caller still has the raw HTTP
    body (attached as .raw) to log, even when this is raised."""

    def __init__(self, message, raw=None):
        super().__init__(message)
        self.raw = raw
