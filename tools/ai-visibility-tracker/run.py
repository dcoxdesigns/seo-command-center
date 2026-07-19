#!/usr/bin/env python3
"""SF5 AI Visibility Tracker — weekly runner.

Usage:
    python run.py                       # dry run: shows the plan, no API calls, no cost
    python run.py --run                 # actually calls ChatGPT/Perplexity/Gemini, spends money
    python run.py --run --client acme   # only run one client (clients/<slug>/ai-visibility-tracker.json)

Requires API keys as environment variables — copy .env.example to .env and
fill in real keys (loaded automatically). Missing a key skips that platform
with a warning; it doesn't stop the run for the other platforms.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from tracker.env import load_env
from tracker.runner import run

load_env(os.path.join(os.path.dirname(__file__), ".env"))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", action="store_true", help="Actually execute (default is dry run).")
    parser.add_argument("--client", action="append", dest="clients",
                         help="Only run this client slug (clients/<slug>/). Repeatable.")
    args = parser.parse_args()

    run(client_slugs=args.clients, dry_run=not args.run)


if __name__ == "__main__":
    main()
