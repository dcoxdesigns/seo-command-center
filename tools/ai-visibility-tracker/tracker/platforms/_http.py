"""Shared HTTP POST helper — urllib only, no requests dependency."""

import json
import urllib.error
import urllib.request

from .base import PlatformError


def post_json(url, headers, body, timeout=60):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw_body = e.read().decode("utf-8", errors="replace")
        try:
            raw = json.loads(raw_body)
        except json.JSONDecodeError:
            raw = {"raw_text": raw_body}
        raise PlatformError(f"HTTP {e.code} from {url}: {raw_body[:300]}", raw=raw, status_code=e.code) from e
    except urllib.error.URLError as e:
        raise PlatformError(f"Network error calling {url}: {e}") from e
