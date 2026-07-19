#!/usr/bin/env python3
"""Generate a printable/emailable Markdown AI Visibility report for one client.

Usage:
    python client_report_cli.py --client acme          # save to clients/acme/reports/
    python client_report_cli.py --client acme --stdout  # print instead of saving
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from tracker.client_report import generate_markdown, save_report


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--client", required=True, help="Client slug (clients/<slug>/).")
    parser.add_argument("--stdout", action="store_true", help="Print instead of saving to reports/.")
    args = parser.parse_args()

    try:
        if args.stdout:
            print(generate_markdown(args.client))
        else:
            path = save_report(args.client)
            print(f"Saved: {path}")
    except ValueError as e:
        sys.exit(str(e))


if __name__ == "__main__":
    main()
