"""Perplexity — Sonar API (OpenAI-chat-completions-compatible, citations included free).

NOT LIVE-TESTED — built from documented API shape, no Perplexity key was
available while writing this. Verify against https://docs.perplexity.ai
before relying on it.
"""

import os

from . import _http
from .base import PlatformError, PlatformResponse

NAME = "perplexity"
ENV_KEY = "PERPLEXITY_API_KEY"
URL = "https://api.perplexity.ai/chat/completions"
MODEL = os.environ.get("PERPLEXITY_MODEL", "sonar")


def call(prompt, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
    }
    raw = _http.post_json(URL, headers, body)

    try:
        text = raw["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        raise PlatformError(f"Unexpected response shape from Perplexity: {e}", raw=raw)

    citation_urls = raw.get("citations", []) or []
    return PlatformResponse(text=text, citation_urls=citation_urls, raw=raw)
