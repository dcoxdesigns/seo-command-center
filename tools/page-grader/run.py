#!/usr/bin/env python3
"""SF5 Page Grader — automated five-lever page review.

Usage:
    python run.py --url https://example.com/page                    # dry run
    python run.py --url https://example.com/page --run               # actually calls Claude, spends money
    python run.py --url https://example.com/page --run --client acme # saves to clients/acme/reports/
    python run.py --url https://example.com/page --run --query "best 5-axis CNC machine for aerospace"
    python run.py --file page.html --run
    python run.py --text "paste raw page copy here" --run

Requires ANTHROPIC_API_KEY — copy .env.example to .env and fill in a real key.
Without --client, the report prints to stdout instead of saving (there's
nowhere to save it to, and no client-facts.md to check the page against).
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from grader.env import load_env
from grader.pipeline import review

load_env(os.path.join(os.path.dirname(__file__), ".env"))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--url", help="Live page URL to fetch and review.")
    source.add_argument("--file", help="Local HTML file to review.")
    source.add_argument("--text", help="Raw pasted text/content to review (not full HTML).")
    parser.add_argument("--client", help="Client slug (clients/<slug>/) — enables client-facts.md context and saves the report there.")
    parser.add_argument("--page-name", help="Name for the report title (default: page <title> tag or the source).")
    parser.add_argument("--query", help="Declared target query this page should win — if omitted, the AI infers it from the page.")
    parser.add_argument("--run", action="store_true", help="Actually execute (default is dry run).")
    args = parser.parse_args()

    if args.run and "ANTHROPIC_API_KEY" not in os.environ:
        sys.exit("Set ANTHROPIC_API_KEY first (copy .env.example to .env and fill it in).")

    review(
        url=args.url, file=args.file, text=args.text,
        client=args.client, page_name=args.page_name, target_query=args.query,
        dry_run=not args.run,
    )


if __name__ == "__main__":
    main()
