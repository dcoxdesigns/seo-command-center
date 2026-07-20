"""Gemini (Google AI) — Interactions API with Google Search grounding.

Google retired the old `/v1beta/models/{model}:generateContent` REST endpoint
in favor of `/v1beta/interactions` — a different endpoint, header-based auth
(`x-goog-api-key` instead of a `?key=` query param), and a request/response
shape close to OpenAI's Responses API (input + typed tools; steps with a
model_output step holding text + annotations). Live-verified 2026-07-20
against gemini-3.5-flash — the old generateContent endpoint now 404s for
every model tried, not just a renamed one.

One real trap: citation `url` values from this API are Google's own
`vertexaisearch.cloud.google.com/grounding-api-redirect/...` links, not the
actual destination — the real cited domain is in the annotation's `title`
field instead. detection.py/competitors.py both parse a domain out of
whatever URL they're given, so this module reconstructs a synthetic
`https://{title}` URL rather than passing Google's redirect link through —
otherwise every citation would silently resolve to Google's own domain and
citation detection would never match anything.
"""

import os

from . import _http
from .base import PlatformError, PlatformResponse

NAME = "gemini"
ENV_KEY = "GEMINI_API_KEY"
URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")


def call(prompt, api_key):
    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json",
    }
    body = {
        "model": MODEL,
        "input": prompt,
        "tools": [{"type": "google_search"}],
    }
    raw = _http.post_json(URL, headers, body)

    text_parts = []
    citation_urls = []
    try:
        for step in raw.get("steps", []):
            if step.get("type") != "model_output":
                continue
            for content in step.get("content", []):
                if content.get("type") != "text":
                    continue
                text_parts.append(content.get("text", ""))
                for ann in content.get("annotations", []) or []:
                    if ann.get("type") != "url_citation":
                        continue
                    title = ann.get("title")
                    if title:
                        citation_urls.append(f"https://{title}")
    except (AttributeError, TypeError) as e:
        raise PlatformError(f"Unexpected response shape from Gemini: {e}", raw=raw)

    return PlatformResponse(text="\n".join(text_parts), citation_urls=citation_urls, raw=raw)
