#!/usr/bin/env python3
"""Converts an SF5 markdown report (page-review-template.md format, or any
report using the same markdown subset) into a branded, self-contained HTML
file — same treatment as the AI Visibility Tracker's client reports: single
file, SF5 logo/colors inlined, opens in any browser, prints/exports to PDF
cleanly, safe to attach directly to an email.

Hand-rolled markdown parser (headers, hr, tables, ordered/unordered lists,
blockquotes, bold/italic/code, fenced code blocks, paragraphs) — covers the
subset actually used across SF5's report templates. No third-party
dependency, matching the rest of this repo's tools/ convention.

Usage:
    python render.py clients/acme/reports/2026-07-19-page-review-homepage.md
    python render.py clients/acme/reports/2026-07-19-page-review-homepage.md --out custom.html
"""

import argparse
import html as html_lib
import os
import re
import sys

# Same mark used in smallfactory5-site's nav/footer, colors hardcoded rather
# than CSS custom properties — many email clients (Outlook especially) don't
# support var(), and this file needs to survive being pasted/attached there.
SF5_LOGO_SVG = (
    '<svg viewBox="0 0 4000 3000" xmlns="http://www.w3.org/2000/svg" '
    'style="fill-rule:evenodd;clip-rule:evenodd;stroke-linejoin:round;stroke-miterlimit:2;width:56px;height:42px;">'
    '<path fill="#15171B" d="M1894,2704l-1132.394,0l-0,-754.146l375.79,-366.812l0,305.249l398.876,-342.444l0,310.38'
    'l357.727,-311.897l0,-524.33l403.47,0l65.53,-634l162,0l77.817,634l44.654,0l65.53,-634l162,0l77.817,634l64.654,0'
    'l65.53,-634l162,0l77.817,634l256.183,0l0,1685l-1685,0l0,-1Z"/>'
    '<text x="2206px" y="2475px" style="font-family:\'Arial-Black\',\'Arial Black\',sans-serif;font-weight:900;'
    'font-size:1592.889px;fill:#EDECE4;">5</text>'
    '<g transform="matrix(1.435334,0,0,1.435334,687.660465,666.494491)">'
    '<text x="210px" y="1094px" style="font-family:\'Impact\',sans-serif;font-stretch:condensed;'
    'font-size:184.278px;fill:#EDECE4;">SMALL</text>'
    '<text x="210px" y="1260.667px" style="font-family:\'Impact\',sans-serif;font-stretch:condensed;'
    'font-size:184.278px;fill:#EDECE4;">F<tspan x="279.644px 373.223px " y="1260.667px 1260.667px ">AC</tspan>TORY</text>'
    '</g></svg>'
)

_STYLE = """
body{margin:0;background:#EDECE4;color:#15171B;font-family:-apple-system,'IBM Plex Sans',Arial,sans-serif;line-height:1.6;}
.wrap{max-width:820px;margin:0 auto;padding:36px 32px 64px;}
.brand{display:flex;align-items:center;gap:10px;margin-bottom:28px;}
.brand-name{font-weight:700;letter-spacing:0.04em;color:#15171B;font-size:0.85rem;}
h1{font-size:1.6rem;margin:0 0 4px;color:#15171B;}
h2{font-size:1.15rem;color:#2C4870;border-bottom:2px solid #2C4870;padding-bottom:6px;margin:32px 0 14px;}
h3{font-size:1.02rem;color:#15171B;margin:20px 0 8px;}
p{margin:0 0 14px;}
hr{border:none;border-top:1px solid #C9C6BA;margin:28px 0;}
table{width:100%;border-collapse:collapse;margin:14px 0;background:#fff;}
th,td{text-align:left;padding:9px 12px;border:1px solid #C9C6BA;font-size:0.9rem;vertical-align:top;}
th{background:#2C4870;color:#fff;}
ol,ul{padding-left:22px;margin:0 0 16px;}
li{margin-bottom:8px;}
blockquote{border-left:4px solid #C15A2E;background:#fff;padding:14px 20px;margin:0 0 16px;font-style:italic;color:#5B6472;}
code{background:#E1DFD5;padding:2px 5px;border-radius:3px;font-family:'IBM Plex Mono',monospace;font-size:0.88em;}
pre{background:#15171B;color:#EDECE4;padding:16px 18px;border-radius:6px;overflow-x:auto;}
pre code{background:none;color:inherit;padding:0;}
strong{color:#15171B;}
footer{text-align:center;color:#8a8a8a;font-size:0.78rem;margin-top:40px;}
"""


def _inline(text):
    """Bold, italic, inline code, and [text](url) links within a text span."""
    text = html_lib.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def _is_block_start(stripped):
    if stripped.startswith("```"):
        return True
    if re.match(r"^-{3,}$", stripped):
        return True
    if re.match(r"^#{1,6}\s+", stripped):
        return True
    if stripped.startswith(">"):
        return True
    if stripped.startswith("|"):
        return True
    if re.match(r"^\d+\.\s+", stripped):
        return True
    if re.match(r"^[-*]\s+", stripped):
        return True
    return False


def _is_table_separator(stripped):
    return bool(re.match(r"^\|?[\s:|-]+\|?$", stripped)) and "-" in stripped


def markdown_to_html(md_text):
    lines = md_text.split("\n")
    parts = []
    i, n = 0, len(lines)

    while i < n:
        stripped = lines[i].strip()

        if stripped.startswith("```"):
            code_lines = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1
            parts.append(f"<pre><code>{html_lib.escape(chr(10).join(code_lines))}</code></pre>")
            continue

        if re.match(r"^-{3,}$", stripped):
            parts.append("<hr>")
            i += 1
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1))
            parts.append(f"<h{level}>{_inline(m.group(2))}</h{level}>")
            i += 1
            continue

        if stripped.startswith(">"):
            quote_lines = []
            while i < n and lines[i].strip().startswith(">"):
                quote_lines.append(re.sub(r"^\s*>\s?", "", lines[i].strip()))
                i += 1
            parts.append(f"<blockquote>{_inline(' '.join(quote_lines))}</blockquote>")
            continue

        if stripped.startswith("|") and i + 1 < n and _is_table_separator(lines[i + 1].strip()):
            header_cells = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            table = ["<table>", "<tr>" + "".join(f"<th>{_inline(c)}</th>" for c in header_cells) + "</tr>"]
            for row in rows:
                table.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in row) + "</tr>")
            table.append("</table>")
            parts.append("".join(table))
            continue

        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < n and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            parts.append("<ol>" + "".join(f"<li>{_inline(it)}</li>" for it in items) + "</ol>")
            continue

        if re.match(r"^[-*]\s+", stripped):
            items = []
            while i < n and re.match(r"^[-*]\s+", lines[i].strip()):
                items.append(re.sub(r"^[-*]\s+", "", lines[i].strip()))
                i += 1
            parts.append("<ul>" + "".join(f"<li>{_inline(it)}</li>" for it in items) + "</ul>")
            continue

        if stripped == "":
            i += 1
            continue

        para_lines = []
        while i < n and lines[i].strip() != "" and not _is_block_start(lines[i].strip()):
            para_lines.append(lines[i].strip())
            i += 1
        parts.append(f"<p>{_inline(' '.join(para_lines))}</p>")

    return "\n".join(parts)


def wrap_html(body_html, title):
    return (
        f"<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        f"<title>{html_lib.escape(title)}</title><style>{_STYLE}</style></head><body><div class='wrap'>"
        f"<div class='brand'>{SF5_LOGO_SVG}<span class='brand-name'>SMALL FACTORY 5</span></div>"
        f"{body_html}"
        f"<footer>Small Factory 5 &mdash; Built to be cited.</footer>"
        f"</div></body></html>"
    )


def render_file(md_path, out_path=None):
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()
    title_match = re.search(r"^#\s+(.*)$", md_text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else os.path.basename(md_path)
    html_doc = wrap_html(markdown_to_html(md_text), title)
    if out_path is None:
        out_path = os.path.splitext(md_path)[0] + ".html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_doc)
    return out_path


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("markdown_file", help="Path to the SF5 report markdown file to convert.")
    parser.add_argument("--out", help="Output HTML path (default: same name, .html extension).")
    args = parser.parse_args()
    if not os.path.exists(args.markdown_file):
        sys.exit(f"File not found: {args.markdown_file}")
    out_path = render_file(args.markdown_file, args.out)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
