"""Gets page HTML/text from a URL, a local file, or raw pasted text."""

import urllib.error
import urllib.request


class FetchError(Exception):
    pass


def fetch_url(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (SF5 Page Grader)"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.read().decode(charset, errors="replace")
    except urllib.error.HTTPError as e:
        raise FetchError(f"HTTP {e.code} fetching {url}") from e
    except urllib.error.URLError as e:
        raise FetchError(f"Could not reach {url}: {e}") from e


def fetch_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
