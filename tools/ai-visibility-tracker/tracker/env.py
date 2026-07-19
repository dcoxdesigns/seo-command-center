"""Minimal .env loader — stdlib only, no python-dotenv dependency.

Reads KEY=VALUE lines from a .env file and sets them in os.environ if not
already set there. Real environment variables always win over the file.
"""

import os


def load_env(path):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)
