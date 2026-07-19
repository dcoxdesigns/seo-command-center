"""SQLite storage for tracker runs — single file, no external DB.

Schema:
    runs(id, client, platform, prompt, timestamp, replicate, mentioned, cited,
         citation_urls, raw_response_path)

`timestamp` is the run's start time (ISO 8601, one shared value per runner.py
invocation) — every row from the same run shares it, so grouping by timestamp
is how you get "this run" vs. "a prior run" for trend reporting.

`replicate` (1..N) distinguishes the repeated calls the sampling methodology
makes for the same prompt in the same run — see runner.REPLICATES_PER_PROMPT.
A single query on a single day is a sample size of one; storing each repeat
as its own row (not just an aggregate) keeps the raw receipts if a client
questions a score, and lets reports show "cited 2 of 3 times" nuance instead
of a flattened binary.
"""

import json
import os
import sqlite3

# Overridable via env var so tests/scratch scripts never touch real client
# data by pointing at the same file (this bit — the hard way, once).
DB_PATH = os.environ.get(
    "AI_TRACKER_DB_PATH",
    os.path.join(os.path.dirname(__file__), "..", "data", "tracker.db"),
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client TEXT NOT NULL,
    platform TEXT NOT NULL,
    prompt TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    replicate INTEGER NOT NULL DEFAULT 1,
    mentioned INTEGER NOT NULL,
    cited INTEGER NOT NULL,
    citation_urls TEXT,
    raw_response_path TEXT
);
CREATE INDEX IF NOT EXISTS idx_runs_client_platform_ts ON runs (client, platform, timestamp);
"""


def connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    # Self-migrate DBs created before the `replicate` column existed.
    try:
        conn.execute("ALTER TABLE runs ADD COLUMN replicate INTEGER NOT NULL DEFAULT 1")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # column already exists
    return conn


def insert_run(conn, *, client, platform, prompt, timestamp, replicate, mentioned, cited,
                citation_urls, raw_response_path):
    conn.execute(
        """INSERT INTO runs
           (client, platform, prompt, timestamp, replicate, mentioned, cited, citation_urls, raw_response_path)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (client, platform, prompt, timestamp, replicate, int(mentioned), int(cited),
         json.dumps(citation_urls or []), raw_response_path),
    )
    conn.commit()


def distinct_timestamps(conn, client):
    """Every run timestamp for a client, most recent first."""
    rows = conn.execute(
        "SELECT DISTINCT timestamp FROM runs WHERE client = ? ORDER BY timestamp DESC",
        (client,),
    ).fetchall()
    return [r["timestamp"] for r in rows]


def rows_for_run(conn, client, timestamp, platform=None):
    if platform:
        return conn.execute(
            "SELECT * FROM runs WHERE client = ? AND timestamp = ? AND platform = ?",
            (client, timestamp, platform),
        ).fetchall()
    return conn.execute(
        "SELECT * FROM runs WHERE client = ? AND timestamp = ?",
        (client, timestamp),
    ).fetchall()


def prompt_matrix(conn, client, timestamp):
    """{prompt: {platform: [rows]}} for one run — one list per cell since each
    prompt/platform combination has REPLICATES_PER_PROMPT rows, not one."""
    matrix = {}
    for row in rows_for_run(conn, client, timestamp):
        matrix.setdefault(row["prompt"], {}).setdefault(row["platform"], []).append(row)
    return matrix


def distinct_clients(conn):
    rows = conn.execute("SELECT DISTINCT client FROM runs ORDER BY client").fetchall()
    return [r["client"] for r in rows]
