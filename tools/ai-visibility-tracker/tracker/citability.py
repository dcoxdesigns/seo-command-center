"""Citability Index — SF5's 0-100 score for AI-answer visibility.

    Citability Index = (Mention Rate x 40) + (Citation Rate x 60)

Citation is weighted higher than mention: being cited as a source means the
page itself did the work, not just brand-name recognition. Rates are
fractions (0.0-1.0) internally, so the blend tops out at 100.
"""

from . import db

BANDS = [
    (0, 25, "Low visibility"),
    (26, 50, "Emerging"),
    (51, 75, "Solid"),
    (76, 100, "Strong"),
]

BAND_DESCRIPTIONS = {
    "Low visibility": "Brand rarely surfaces; likely a content/structure gap (Citability lever work needed).",
    "Emerging": "Occasional mentions, few citations. Room to push toward source-level visibility.",
    "Solid": "Consistently surfacing, regularly cited. Maintenance and monitoring for drop-offs.",
    "Strong": "Brand is a go-to source across most tracked queries — rare at this stage, useful as an aspirational benchmark.",
}

# Open question from the build brief, resolved with a starting default:
# flag a client in the weekly report if their blended Citability Index drops
# by at least this many points since the previous run, OR drops into a lower
# band entirely. Tune this once a few weeks of real trend data exist.
ALERT_DROP_THRESHOLD = 15


def band(score):
    for low, high, label in BANDS:
        if low <= score <= high:
            return label
    return "Unknown"


def index_from_rows(rows):
    """rows: iterable of objects with .mentioned / .cited (or dict-like with those keys)."""
    rows = list(rows)
    total = len(rows)
    if total == 0:
        return {"mention_rate": 0.0, "citation_rate": 0.0, "citability_index": 0.0, "n": 0}
    mentioned = sum(1 for r in rows if r["mentioned"])
    cited = sum(1 for r in rows if r["cited"])
    mention_rate = mentioned / total
    citation_rate = cited / total
    citability_index = round((mention_rate * 40) + (citation_rate * 60), 1)
    return {
        "mention_rate": round(mention_rate, 3),
        "citation_rate": round(citation_rate, 3),
        "citability_index": citability_index,
        "n": total,
    }


def client_report_for_run(conn, client, timestamp, platforms):
    """Per-platform breakdown plus the blended average across platforms for one run."""
    per_platform = {}
    for platform in platforms:
        rows = db.rows_for_run(conn, client, timestamp, platform=platform)
        per_platform[platform] = index_from_rows(rows)

    all_rows = db.rows_for_run(conn, client, timestamp)
    blended = index_from_rows(all_rows)

    return {
        "client": client,
        "timestamp": timestamp,
        "per_platform": per_platform,
        "blended": blended,
        "band": band(blended["citability_index"]),
    }


def compare_to_previous(conn, client, platforms):
    """Returns (latest_report, previous_report_or_None, flagged: bool, delta: float|None)
    for the most recent two runs of a client. flagged is True if the blended
    index dropped by >= ALERT_DROP_THRESHOLD or moved into a lower band."""
    timestamps = db.distinct_timestamps(conn, client)
    if not timestamps:
        return None, None, False, None

    latest = client_report_for_run(conn, client, timestamps[0], platforms)
    if len(timestamps) < 2:
        return latest, None, False, None

    previous = client_report_for_run(conn, client, timestamps[1], platforms)
    delta = round(latest["blended"]["citability_index"] - previous["blended"]["citability_index"], 1)
    band_dropped = BANDS.index(next(b for b in BANDS if b[2] == latest["band"])) < \
        BANDS.index(next(b for b in BANDS if b[2] == previous["band"]))
    flagged = delta <= -ALERT_DROP_THRESHOLD or band_dropped
    return latest, previous, flagged, delta
