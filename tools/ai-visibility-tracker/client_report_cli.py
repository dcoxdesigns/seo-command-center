#!/usr/bin/env python3
"""Generate a printable/emailable AI Visibility report for one client.

Usage:
    python client_report_cli.py --client acme                # saves Markdown to clients/acme/reports/
    python client_report_cli.py --client acme --html          # saves a self-contained HTML version instead
    python client_report_cli.py --client acme --html --stdout # print the HTML instead of saving
    python client_report_cli.py --client acme --stdout        # print the Markdown instead of saving

The HTML version is the one to actually email or attach — it's a single
self-contained file (logo embedded, no external assets), opens in any
browser, and prints/exports to PDF cleanly. Plain Markdown doesn't reliably
render images or tables once it leaves a markdown-aware editor.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from tracker.client_report import generate_html, generate_markdown, save_html_report, save_report


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--client", required=True, help="Client slug (clients/<slug>/).")
    parser.add_argument("--html", action="store_true", help="Generate the HTML version instead of Markdown.")
    parser.add_argument("--stdout", action="store_true", help="Print instead of saving to reports/.")
    args = parser.parse_args()

    try:
        if args.html:
            if args.stdout:
                print(generate_html(args.client))
            else:
                path = save_html_report(args.client)
                print(f"Saved: {path}")
        else:
            if args.stdout:
                print(generate_markdown(args.client))
            else:
                path = save_report(args.client)
                print(f"Saved: {path}")
    except ValueError as e:
        sys.exit(str(e))


if __name__ == "__main__":
    main()
