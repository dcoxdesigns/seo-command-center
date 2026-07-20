#!/usr/bin/env python3
"""Push each client's latest Citability Index into Redis, so the page-review
tool on smallfactory5-site can show it alongside a page review for that
client. Run this after a tracker run (run.py --run) whenever you want the
site's copy refreshed — it's a separate, manual step, not auto-chained.

The Redis key is citability:<client>, where <client> is the exact display
name from clients/<slug>/ai-visibility-tracker.json ("client" field) — that
string must match exactly what gets typed into the page-review tool's
Client Name field for the lookup to find it.

Usage:
    python export_citability.py --client acme
    python export_citability.py --all
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from tracker import citability, db, env
from tracker.config import load_all_client_configs, load_client_config
from tracker.platforms import ALL as ALL_PLATFORMS
from tracker.redis_export import set_json

env.load_env(os.path.join(os.path.dirname(__file__), ".env"))

PLATFORM_NAMES = [p.NAME for p in ALL_PLATFORMS]


def export_one(conn, cfg):
    timestamps = db.distinct_timestamps(conn, cfg.client)
    if not timestamps:
        print(f"  [skip] {cfg.client}: no tracker runs yet.")
        return False

    report = citability.client_report_for_run(conn, cfg.client, timestamps[0], PLATFORM_NAMES)
    payload = {
        "client": cfg.client,
        "citability_index": report["blended"]["citability_index"],
        "band": report["band"],
        "mention_rate": report["blended"]["mention_rate"],
        "citation_rate": report["blended"]["citation_rate"],
        "n": report["blended"]["n"],
        "run_timestamp": timestamps[0],
    }
    set_json(f"citability:{cfg.client}", payload)
    print(f"  [ok] {cfg.client}: {payload['citability_index']}/100 ({payload['band']}) — pushed.")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--client", help="Client slug (clients/<slug>/).")
    group.add_argument("--all", action="store_true", help="Export every configured client.")
    args = parser.parse_args()

    if args.all:
        configs = load_all_client_configs()
    else:
        cfg = load_client_config(args.client)
        if cfg is None:
            sys.exit(f"No config found for client slug {args.client!r}.")
        configs = [cfg]

    if not configs:
        sys.exit("No client configs found (clients/<name>/ai-visibility-tracker.json).")

    conn = db.connect()
    try:
        for cfg in configs:
            export_one(conn, cfg)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
