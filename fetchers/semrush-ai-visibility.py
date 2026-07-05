#!/usr/bin/env python3
"""Pull AI-visibility data from the Semrush AI Visibility API into data/ai-visibility/semrush/.

This is the "fetcher" pattern: an API that drops data into the project so the agent can
read and cross-reference it. No third-party packages — standard library only.

Usage:
    export SEMRUSH_API_KEY=...            # your key (Semrush AI Visibility API access required)
    python fetchers/semrush-ai-visibility.py example.com 2026-05 US
    python fetchers/semrush-ai-visibility.py example.com 2026-05 US --run

If you don't have API access, skip this — drop a CSV export into data/ai-visibility/ instead.
The class works either way.

Cost note: each report costs 300-1000 API units. This script makes 4 calls (~1,800 units).
Check your balance: https://www.semrush.com/users/countapiunits.html?key=KEY
"""

import json
import os
import re
import sys
import urllib.parse
import urllib.request

BASE = "https://api.semrush.com/apis/v4/ai/visibility/v1"

# report name -> endpoint path. The brand reports take domain/country/month.
REPORTS = {
    "overview": "brands/stats",
    "topics": "brands/topics/stats",
    "prompts": "brands/prompts/stats",
    "cited": "brands/cited-pages/stats",
}


def fetch(path, params):
    url = f"{BASE}/{path}?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=60) as resp:
        return json.load(resp)


def main():
    args = [arg for arg in sys.argv[1:] if arg != "--run"]
    should_run = "--run" in sys.argv[1:]

    domain = args[0] if len(args) > 0 else "example.com"
    month = args[1] if len(args) > 1 else "2026-05"
    country = args[2] if len(args) > 2 else "US"   # API wants "country", not "region"
    country = country.upper()

    if not re.fullmatch(r"\d{4}-\d{2}", month):
        sys.exit("Month must use YYYY-MM format, e.g. 2026-05.")

    if not re.fullmatch(r"[A-Z]{2}", country):
        sys.exit("Country must be a two-letter country code, e.g. US.")

    if not should_run:
        print("Dry run: would make 4 Semrush AI Visibility API calls.")
        print("Estimated cost: roughly 1,800 API units.")
        print(f"Domain: {domain}")
        print(f"Month: {month}")
        print(f"Country: {country}")
        print("Re-run with --run to execute.")
        return

    key = os.environ.get("SEMRUSH_API_KEY")
    if not key:
        sys.exit("Set SEMRUSH_API_KEY first (export SEMRUSH_API_KEY=...).")

    out_dir = os.path.join(os.path.dirname(__file__), "..", "data", "ai-visibility", "semrush")
    os.makedirs(out_dir, exist_ok=True)

    slug = domain.replace(".", "-").replace("/", "-")
    for name, path in REPORTS.items():
        data = fetch(path, {"key": key, "domain": domain, "country": country, "month": month})
        if not data.get("meta", {}).get("success", True):
            print(f"  {name}: API returned an error -> {data.get('meta')}")
            continue
        dest = os.path.join(out_dir, f"{slug}-{name}-{month}.json")
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"  {name}: saved {dest}")

    print("Done. The agent can now read data/ai-visibility/semrush/ and cross-reference it.")
    print("Saved real API output under data/. Do not rename these files to sample-* unless the data is synthetic.")


if __name__ == "__main__":
    main()
