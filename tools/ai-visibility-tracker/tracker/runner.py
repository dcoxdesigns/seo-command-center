"""Orchestration: for each client -> for each prompt -> for each platform,
call the API, detect mentions/citations, log the raw response, store a row.

Dry-run by default (like fetchers/semrush-ai-visibility.py) — this one spends
real money across three APIs, so an accidental invocation should never bill
anything without an explicit --run.
"""

import datetime
import json
import os
import re
import sys
import time

from . import citability, db, detection
from .config import load_all_client_configs, load_client_config
from .platforms import ALL as ALL_PLATFORMS

# Rough blended per-call cost, derived from the brief's ~$10-20/month at
# ~600 calls/month across all three platforms combined. For the dry-run
# estimate only — not exact billing, check each provider's dashboard for that.
EST_COST_PER_CALL_LOW = 0.017
EST_COST_PER_CALL_HIGH = 0.033

SLEEP_BETWEEN_CALLS_SECONDS = 1.5


def _slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def _available_platforms():
    """Platforms with an API key actually set. Missing keys are skipped with
    a warning rather than failing the whole run."""
    available = []
    for platform in ALL_PLATFORMS:
        if os.environ.get(platform.ENV_KEY):
            available.append(platform)
        else:
            print(f"  [skip] {platform.NAME}: {platform.ENV_KEY} not set")
    return available


def plan(client_slugs=None):
    """Returns (configs, platforms, total_calls) without calling anything."""
    if client_slugs:
        configs = [c for c in (load_client_config(s) for s in client_slugs) if c]
    else:
        configs = load_all_client_configs()
    platforms = _available_platforms()
    total_calls = sum(len(c.prompts) for c in configs) * len(platforms)
    return configs, platforms, total_calls


def run(client_slugs=None, dry_run=True):
    configs, platforms, total_calls = plan(client_slugs)

    if not configs:
        print("No client configs found (clients/<name>/ai-visibility-tracker.json). Nothing to do.")
        return

    if dry_run:
        print("Dry run: would make the following calls (no API calls, no cost, nothing stored).\n")
        for cfg in configs:
            print(f"  {cfg.client} ({cfg.slug}): {len(cfg.prompts)} prompts x {len(platforms)} platforms "
                  f"= {len(cfg.prompts) * len(platforms)} calls")
        low = total_calls * EST_COST_PER_CALL_LOW
        high = total_calls * EST_COST_PER_CALL_HIGH
        print(f"\nTotal: {total_calls} calls across {len(configs)} client(s) and {len(platforms)} platform(s).")
        print(f"Estimated cost: ${low:.2f}-${high:.2f} (rough — check provider dashboards for actuals).")
        print("Re-run with --run to execute.")
        return

    run_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    conn = db.connect()
    print(f"Run started {run_timestamp} — {total_calls} calls planned.\n")

    for cfg in configs:
        print(f"{cfg.client} ({cfg.slug})")
        run_dir = os.path.join(cfg.data_dir, run_timestamp.replace(":", "-"))
        os.makedirs(run_dir, exist_ok=True)

        for platform in platforms:
            api_key = os.environ[platform.ENV_KEY]
            for prompt in cfg.prompts:
                try:
                    response = platform.call(prompt, api_key)
                except Exception as e:
                    print(f"  [error] {platform.NAME} / {prompt!r}: {e}")
                    raw = getattr(e, "raw", None)
                    if raw is not None:
                        err_path = os.path.join(run_dir, f"{platform.NAME}-{_slugify(prompt)}-ERROR.json")
                        with open(err_path, "w", encoding="utf-8") as f:
                            json.dump(raw, f, indent=2)
                    time.sleep(SLEEP_BETWEEN_CALLS_SECONDS)
                    continue

                raw_path = os.path.join(run_dir, f"{platform.NAME}-{_slugify(prompt)}.json")
                with open(raw_path, "w", encoding="utf-8") as f:
                    json.dump(response.raw, f, indent=2)

                # cfg.client (the display name) always counts as a variant too, so a
                # config that only lists extra spellings in brand_variants doesn't
                # silently miss the base name.
                mentioned = detection.is_mentioned(response.text, cfg.domain, [cfg.client] + cfg.brand_variants)
                matched_citations = detection.cited_urls(response.citation_urls, cfg.domain)
                cited = len(matched_citations) > 0

                db.insert_run(
                    conn,
                    client=cfg.client,
                    platform=platform.NAME,
                    prompt=prompt,
                    timestamp=run_timestamp,
                    mentioned=mentioned,
                    cited=cited,
                    # store every citation URL returned, not just the ones matching
                    # this client — competitors.py needs the full list to show who
                    # got cited instead when this client didn't.
                    citation_urls=response.citation_urls,
                    raw_response_path=raw_path,
                )
                flag = "CITED" if cited else ("mentioned" if mentioned else "-")
                print(f"  {platform.NAME:12} {flag:9} {prompt[:60]}")
                time.sleep(SLEEP_BETWEEN_CALLS_SECONDS)

    conn.close()
    print(f"\nDone. Run timestamp: {run_timestamp}")
    print("Run report_cli.py to see Citability Index results.")
