"""Gemini (Google AI) — generateContent with Search grounding.

NOT LIVE-TESTED — built from documented API shape, no Gemini key was
available while writing this. Verify against
https://ai.google.dev/gemini-api/docs/grounding before relying on it,
especially: the "google_search" tool key casing and the model name below —
both are areas Google has changed field names in before.
"""

import os

from . import _http
from .base import PlatformError, PlatformResponse

NAME = "gemini"
ENV_KEY = "GEMINI_API_KEY"
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")


def call(prompt, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"google_search": {}}],
    }
    raw = _http.post_json(url, headers, body)

    try:
        candidate = raw["candidates"][0]
        parts = candidate.get("content", {}).get("parts", [])
        text = "\n".join(p.get("text", "") for p in parts)
    except (KeyError, IndexError, TypeError) as e:
        raise PlatformError(f"Unexpected response shape from Gemini: {e}", raw=raw)

    citation_urls = []
    grounding_chunks = candidate.get("groundingMetadata", {}).get("groundingChunks", []) or []
    for chunk in grounding_chunks:
        web = chunk.get("web") or {}
        if web.get("uri"):
            citation_urls.append(web["uri"])

    return PlatformResponse(text=text, citation_urls=citation_urls, raw=raw)
