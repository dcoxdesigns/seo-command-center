"""Classifies whether a stored AI response recommends the client outright,
merely names them among others, or doesn't mention them at all — see
ci-recommendation-rate-addendum.md. Citation and mention both just count
whether the brand was *named*; they don't capture whether the AI actually
told the user to pick it over competitors named in the same response.

Only ever called when a response already mentions the client (see runner.py)
— an unmentioned response is trivially "absent" and needs no LLM call to
confirm, which keeps the added cost proportional to the hit rate rather than
the full call volume. This is a classification pass on text already in hand
(no new calls to the AI search platforms themselves), same convention as the
rest of this tool: stdlib only, no third-party dependency.
"""

import json
import os
import urllib.error
import urllib.request

URL = "https://api.anthropic.com/v1/messages"
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")
MAX_TOKENS = 20

PROMPT_TEMPLATE = """An AI assistant was asked: "{prompt}"

It responded:
---
{response_text}
---

Does this response present "{client}" as THE recommended choice, or one of a
short explicit shortlist (3 or fewer) it clearly endorses over the
alternatives? Or is "{client}" merely named, cited, or listed among other
options with no differentiating endorsement?

Reply with exactly one word, nothing else:
RECOMMENDED — singled out as the pick, "best," top choice, or in a clearly
endorsed shortlist of 3 or fewer.
PRESENT — named, cited, or listed among options with no endorsement.
"""


def classify(prompt, response_text, client, api_key):
    """Returns 'recommended' or 'present'."""
    body = {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "messages": [{
            "role": "user",
            "content": PROMPT_TEMPLATE.format(prompt=prompt, response_text=(response_text or "")[:6000], client=client),
        }],
    }
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    req = urllib.request.Request(URL, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} from Claude API: {e.read().decode('utf-8', errors='replace')[:300]}") from e

    text = "".join(block.get("text", "") for block in raw.get("content", []) if block.get("type") == "text").strip().upper()
    return "recommended" if "RECOMMENDED" in text else "present"
