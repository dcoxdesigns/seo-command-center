"""Reads the actual SF5 methodology docs at runtime — the AI prompt is built
from config/five-lever-framework.md and config/brand-voice.md directly, not a
copy pasted into this tool's code. If the framework doc changes, this tool's
scoring criteria change with it automatically, with nothing to keep in sync.
"""

import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
CONFIG_DIR = os.path.join(REPO_ROOT, "config")
CLIENTS_DIR = os.path.join(REPO_ROOT, "clients")


def _read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def five_lever_framework():
    return _read(os.path.join(CONFIG_DIR, "five-lever-framework.md"))


def brand_voice():
    return _read(os.path.join(CONFIG_DIR, "brand-voice.md"))


def client_facts(client_slug):
    if not client_slug:
        return None
    path = os.path.join(CLIENTS_DIR, client_slug, "client-facts.md")
    if not os.path.exists(path):
        return None
    return _read(path)
