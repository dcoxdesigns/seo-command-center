"""Finds and persists prior reviews of the same page, so a re-review can
report real score deltas and check whether previously recommended fixes
actually shipped — implements the reference process's own re-grade
cadence: diagnose once, batch fixes, verify once against the live page
(not the spec handed over), and report each fix's real outcome honestly
(shipped / partial / not shipped), not assumed uniform.

Matched by exact URL — the same page reviewed twice. --file/--text runs
have no stable identity to match against, so re-grade only ever triggers
for --url runs.
"""

import glob
import json
import os
import re


def _slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def _sidecar_dir(client_slug, clients_dir):
    return os.path.join(clients_dir, client_slug, "reports")


def save_sidecar(client_slug, clients_dir, *, url, page_name, date, ai_result):
    """Saves the raw AI result alongside the markdown report so a future
    run can diff against it — the markdown itself isn't reliably
    re-parseable, this is the structured record."""
    reports_dir = _sidecar_dir(client_slug, clients_dir)
    os.makedirs(reports_dir, exist_ok=True)

    path = os.path.join(reports_dir, f"{date}-page-review-{_slugify(page_name)}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"url": url, "page_name": page_name, "date": date, "ai_result": ai_result}, f, indent=2)
    return path


def find_previous_review(client_slug, clients_dir, url):
    """Most recent prior sidecar for this exact URL, or None. Scans all
    saved sidecars for this client — small N in practice (one client's
    reviewed pages), no index needed."""
    if not url:
        return None
    reports_dir = _sidecar_dir(client_slug, clients_dir)
    candidates = []
    for path in glob.glob(os.path.join(reports_dir, "*.json")):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        if data.get("url") == url:
            candidates.append((data.get("date", ""), data))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0])
    return candidates[-1][1]
