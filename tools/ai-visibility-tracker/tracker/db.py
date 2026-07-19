"""SQLite storage for tracker runs — single file, no external DB.

Schema (matches the build brief):
    runs(id, client, platform, prompt, timestamp, mentioned, cited,
         citation_urls, raw_response_path)

`timestamp` is the run's start time (ISO 8601, one shared value per runner.py
invocation) — every row from the same weekly run shares it, so grouping by
timestamp is how you get "this run" vs. "a prior run" for trend reporting.
"""

import json
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "tracker.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client TEXT NOT NULL,
    platform TEXT NOT NULL,
    prompt TEXT NOT NULL,
    timestamp TEXT NOT NULL,
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
    return conn


def insert_run(conn, *, client, platform, prompt, timestamp, mentioned, cited,
                citation_urls, raw_response_path):
    conn.execute(
        """INSERT INTO runs
           (client, platform, prompt, timestamp, mentioned, cited, citation_urls, raw_response_path)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (client, platform, prompt, timestamp, int(mentioned), int(cited),
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


def distinct_clients(conn):
    rows = conn.execute("SELECT DISTINCT client FROM runs ORDER BY client").fetchall()
    return [r["client"] for r in rows]
