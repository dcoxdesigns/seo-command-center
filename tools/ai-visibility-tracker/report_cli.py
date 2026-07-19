#!/usr/bin/env python3
"""Print Citability Index reports from stored run data.

Usage:
    python report_cli.py                # every client
    python report_cli.py --client acme  # one client (clients/<slug>/ name)
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from tracker.report import print_all_reports


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--client", help="Only report this client slug.")
    args = parser.parse_args()
    print_all_reports(client_slug_filter=args.client)


if __name__ == "__main__":
    main()
