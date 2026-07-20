"""Structural facts pulled directly from HTML parsing — no AI judgment involved.
These feed the AI-judge prompt as ground truth (so it isn't re-guessing things
a parser can just verify) and directly answer the Structured Clarity lever's
mechanical checks (heading hierarchy, schema presence).
"""

import json
from html.parser import HTMLParser


class _PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = None
        self.meta_description = None
        self.canonical = None
        self.has_viewport = False
        self.headings = []  # [(level, text)]
        self.jsonld_blocks = []  # raw strings
        self.images = []  # [{"src": ..., "has_alt": bool}]
        self.text_chunks = []

        self._in_title = False
        self._in_heading_level = None
        self._heading_text = []
        self._in_jsonld = False
        self._jsonld_text = []
        self._skip_text_tags = {"script", "style", "noscript"}
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in self._skip_text_tags:
            self._skip_depth += 1
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            name = (attrs.get("name") or "").lower()
            if name == "description":
                self.meta_description = attrs.get("content", "")
            if name == "viewport":
                self.has_viewport = True
        elif tag == "link" and (attrs.get("rel") or "").lower() == "canonical":
            self.canonical = attrs.get("href")
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._in_heading_level = int(tag[1])
            self._heading_text = []
        elif tag == "script" and (attrs.get("type") or "").lower() == "application/ld+json":
            self._in_jsonld = True
            self._jsonld_text = []
        elif tag == "img":
            self.images.append({
                "src": attrs.get("src", ""),
                "has_alt": bool((attrs.get("alt") or "").strip()),
            })

    def handle_endtag(self, tag):
        if tag in self._skip_text_tags:
            self._skip_depth = max(0, self._skip_depth - 1)
        if tag == "title":
            self._in_title = False
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self._in_heading_level:
            self.headings.append((self._in_heading_level, "".join(self._heading_text).strip()))
            self._in_heading_level = None
        elif tag == "script" and self._in_jsonld:
            self.jsonld_blocks.append("".join(self._jsonld_text))
            self._in_jsonld = False

    def handle_data(self, data):
        if self._in_title:
            self.title = (self.title or "") + data
        if self._in_heading_level:
            self._heading_text.append(data)
        if self._in_jsonld:
            self._jsonld_text.append(data)
        elif self._skip_depth == 0:
            stripped = data.strip()
            if stripped:
                self.text_chunks.append(stripped)


def heading_jumps(headings):
    """Number of times a heading level increases by more than 1 from the
    previous heading (an H2 straight to an H4, skipping H3)."""
    jumps = 0
    prev_level = None
    for level, _text in headings:
        if prev_level is not None and level > prev_level + 1:
            jumps += 1
        prev_level = level
    return jumps


def parse_jsonld(blocks):
    parsed = []
    errors = 0
    for raw in blocks:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            errors += 1
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if isinstance(item, dict) and "@type" in item:
                parsed.append(item)
    return parsed, errors


def analyze(html_text):
    parser = _PageParser()
    parser.feed(html_text)

    jsonld_items, jsonld_errors = parse_jsonld(parser.jsonld_blocks)
    schema_types = sorted({item["@type"] for item in jsonld_items if isinstance(item.get("@type"), str)})

    h1_count = sum(1 for level, _ in parser.headings if level == 1)
    word_count = len(" ".join(parser.text_chunks).split())
    total_images = len(parser.images)
    images_missing_alt = sum(1 for img in parser.images if not img["has_alt"])

    return {
        "title": (parser.title or "").strip() or None,
        "title_length": len((parser.title or "").strip()),
        "meta_description": parser.meta_description,
        "meta_description_length": len(parser.meta_description or ""),
        "canonical": parser.canonical,
        "has_viewport": parser.has_viewport,
        "headings": parser.headings,
        "h1_count": h1_count,
        "heading_jumps": heading_jumps(parser.headings),
        "jsonld_count": len(parser.jsonld_blocks),
        "jsonld_parse_errors": jsonld_errors,
        "schema_types": schema_types,
        "total_images": total_images,
        "images_missing_alt": images_missing_alt,
        "alt_coverage": round((total_images - images_missing_alt) / total_images * 100) if total_images else None,
        "word_count": word_count,
        "visible_text": " ".join(parser.text_chunks),
    }
