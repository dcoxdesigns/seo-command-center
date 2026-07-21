"""Orchestration: fetch -> structural analysis -> AI judgment -> assembled report.

Dry-run by default — this makes one real API call to Claude per review, and
an accidental invocation shouldn't spend money without an explicit --run.
"""

import datetime
import os
import re

from . import ai_judge, config_docs, crawl, fetch, regrade, report, structural

CLIENTS_DIR = config_docs.CLIENTS_DIR

# Rough single-call cost estimate for the dry-run print. Not exact billing —
# check console.anthropic.com for actuals.
EST_COST_LOW = 0.05
EST_COST_HIGH = 0.20


def _slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def review(*, url=None, file=None, text=None, client=None, page_name=None, target_query=None, dry_run=True):
    if sum(x is not None for x in (url, file, text)) != 1:
        raise ValueError("Provide exactly one of url, file, or text.")

    source_label = url or file or "(pasted text)"
    if dry_run:
        print("Dry run: would fetch the page, run structural checks, and make 1 Claude API call.")
        print(f"Source: {source_label}")
        if client:
            print(f"Client: {client}")
        if target_query:
            print(f"Target query: {target_query}")
        else:
            print("Target query: none declared — will be inferred from the page.")
        print(f"Estimated cost: ${EST_COST_LOW:.2f}-${EST_COST_HIGH:.2f} (rough — check console.anthropic.com for actuals).")
        print("Re-run with --run to execute.")
        return None

    if url:
        html_text = fetch.fetch_url(url)
    elif file:
        html_text = fetch.fetch_file(file)
    else:
        html_text = text

    facts = structural.analyze(html_text)
    page_text = facts["visible_text"] or html_text

    print("Structural checks done:")
    print(f"  H1 count: {facts['h1_count']}  |  Heading jumps: {facts['heading_jumps']}  "
          f"|  Schema types: {', '.join(facts['schema_types']) or 'none'}")
    print(f"  Images: {facts['total_images']} ({facts['images_missing_alt']} missing alt)  "
          f"|  Word count: {facts['word_count']}")

    previous_review = None
    if client and url:
        previous_review = regrade.find_previous_review(client, CLIENTS_DIR, url)
        if previous_review:
            print(f"  Found a previous review of this page from {previous_review.get('date')} — re-grading against it.")

    print("Calling Claude to score SEO intent match and the five GEO levers...")
    ai_result, raw = ai_judge.score_page(
        page_text, facts, client_slug=client, target_query=target_query, previous_review=previous_review
    )

    linking = None
    if client:
        crawl_data = crawl.load_crawl(client, CLIENTS_DIR)
        if crawl_data is None:
            print("  (no crawl export found at data/crawl/internal_all.csv — skipping internal-linking analysis)")
        else:
            inbound = crawl.find_inbound_candidates(crawl_data, url, limit=5) if url else []
            outbound = crawl.find_outbound_opportunities(page_text, crawl_data, url, limit=8)
            linking = {"inbound": inbound, "outbound": outbound}
            print(f"  Internal linking: {len(inbound)} inbound candidate(s), {len(outbound)} outbound opportunity(ies)")

    resolved_page_name = page_name or facts["title"] or source_label
    client_name = client or "(no client specified)"
    markdown = report.build_markdown(
        page_name=resolved_page_name,
        client_name=client_name,
        ai_result=ai_result,
        structural_facts=facts,
        linking=linking,
        previous_review=previous_review,
    )

    saved_path = None
    if client:
        reports_dir = os.path.join(CLIENTS_DIR, client, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        today = datetime.date.today().isoformat()
        saved_path = os.path.join(reports_dir, f"{today}-page-review-{_slugify(resolved_page_name)}.md")
        with open(saved_path, "w", encoding="utf-8") as f:
            f.write(markdown)
        print(f"Saved: {saved_path}")
        if url:
            sidecar_path = regrade.save_sidecar(
                client, CLIENTS_DIR, url=url, page_name=resolved_page_name, date=today, ai_result=ai_result
            )
            print(f"Saved re-grade record: {sidecar_path}")
    else:
        print("\nNo --client given — printing instead of saving:\n")
        print(markdown)

    return {"markdown": markdown, "path": saved_path, "structural_facts": facts, "ai_result": ai_result}
