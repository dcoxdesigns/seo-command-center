"""ChatGPT (OpenAI) — Responses API with the web_search tool.

NOT LIVE-TESTED — built from documented API shape, no OpenAI key was available
while writing this. Verify against https://platform.openai.com/docs/api-reference/responses
before relying on it, especially: the exact tool name (web_search vs.
web_search_preview depending on model/account), and the model name below.
"""

import os

from . import _http
from .base import PlatformError, PlatformResponse

NAME = "chatgpt"
ENV_KEY = "OPENAI_API_KEY"
URL = "https://api.openai.com/v1/responses"
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")


def call(prompt, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": MODEL,
        "tools": [{"type": "web_search"}],
        "input": prompt,
    }
    raw = _http.post_json(URL, headers, body)

    text_parts = []
    citation_urls = []
    try:
        for item in raw.get("output", []):
            if item.get("type") != "message":
                continue
            for content in item.get("content", []):
                if content.get("type") in ("output_text", "text"):
                    text_parts.append(content.get("text", ""))
                    for ann in content.get("annotations", []) or []:
                        if ann.get("type") == "url_citation" and ann.get("url"):
                            citation_urls.append(ann["url"])
    except (AttributeError, TypeError) as e:
        raise PlatformError(f"Unexpected response shape from ChatGPT: {e}", raw=raw)

    return PlatformResponse(text="\n".join(text_parts), citation_urls=citation_urls, raw=raw)
