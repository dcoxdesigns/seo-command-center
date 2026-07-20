"""Pushes JSON values to the same Upstash Redis instance smallfactory5-site
reads from — stdlib only (urllib), matching this repo's no-extra-deps
convention (see ai_judge.py's use of urllib for the Anthropic API).

Upstash's REST API accepts a single command as a JSON array POSTed to the
base URL: POST {url} with body ["SET", key, value] and a Bearer token.
"""

import json
import os
import urllib.error
import urllib.request


def _redis_command(*args):
    url = os.environ.get("UPSTASH_REDIS_REST_KV_REST_API_URL")
    token = os.environ.get("UPSTASH_REDIS_REST_KV_REST_API_TOKEN")
    if not url or not token:
        raise RuntimeError(
            "Missing UPSTASH_REDIS_REST_KV_REST_API_URL / _TOKEN — copy these from "
            "smallfactory5-site's .env.local so this exports to the same Redis instance "
            "the site reads from."
        )
    body = json.dumps(list(args)).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Redis REST call failed: HTTP {e.code} {e.read().decode('utf-8', errors='replace')[:300]}") from e


def set_json(key, value):
    """SET key to a JSON-encoded string, no expiry (overwritten each export)."""
    return _redis_command("SET", key, json.dumps(value))
