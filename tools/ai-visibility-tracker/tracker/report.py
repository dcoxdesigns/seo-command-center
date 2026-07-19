"""Reads the SQLite store and prints Citability Index reports.

Per client: this run's Citability Index (blended + per-platform breakdown),
its band, and how it moved since the previous run — flagged if the drop
crosses citability.ALERT_DROP_THRESHOLD or the client fell into a lower band.
"""

from . import citability, db
from .config import load_client_config
from .platforms import ALL as ALL_PLATFORMS

PLATFORM_NAMES = [p.NAME for p in ALL_PLATFORMS]


def print_client_report(conn, client):
    latest, previous, flagged, delta = citability.compare_to_previous(conn, client, PLATFORM_NAMES)
    if latest is None:
        print(f"{client}: no runs yet.")
        return

    print(f"\n{client}")
    print(f"  Run: {latest['timestamp']}")
    print(f"  Citability Index: {latest['blended']['citability_index']} ({latest['band']})")
    for platform, idx in latest["per_platform"].items():
        print(f"    {platform:12} {idx['citability_index']:5.1f}  "
              f"(mention {idx['mention_rate']*100:.0f}%, citation {idx['citation_rate']*100:.0f}%, n={idx['n']})")

    if previous is not None:
        arrow = "up" if delta > 0 else ("down" if delta < 0 else "flat")
        flag_note = "  <-- FLAGGED (check in with client)" if flagged else ""
        print(f"  Trend: {arrow} {delta:+.1f} vs. previous run ({previous['timestamp']}){flag_note}")
    else:
        print("  Trend: first run, no prior data yet.")


def print_all_reports(client_slug_filter=None):
    conn = db.connect()
    if client_slug_filter:
        cfg = load_client_config(client_slug_filter)
        if cfg is None:
            print(f"No config found for clients/{client_slug_filter}/ai-visibility-tracker.json")
            return
        clients = [cfg.client]
    else:
        clients = db.distinct_clients(conn)
    if not clients:
        print("No runs stored yet — run.py --run needs to complete at least once first.")
        return
    for client in clients:
        print_client_report(conn, client)
    conn.close()
