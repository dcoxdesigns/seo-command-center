"""Turns the AI judge's 0-10 per-item scores into a Pass/Needs Work/Fail
display label and a composite 0-100 score per scorecard (SEO Intent Match,
GEO five levers) — two numbers, reported side by side, never blended into
one, per the reference process this was modeled on (a page scoring
34/100 SEO and 22/100 GEO is a different situation than one scoring
28/100 on both, and blending them would hide that).

The 0-10 score is the source of truth; the label is derived from it, not a
second independent judgment the AI makes — keeps the label and the number
from ever disagreeing with each other.
"""


def score_label(score):
    if score is None:
        return "N/A"
    if score >= 8:
        return "Pass"
    if score >= 4:
        return "Needs Work"
    return "Fail"


def composite_score(items, keys):
    """items: dict of key -> {"score": int, ...}. keys: which entries to
    include. Returns an int 0-100, or None if no scored items are present."""
    scores = [items.get(k, {}).get("score") for k in keys]
    scores = [s for s in scores if isinstance(s, (int, float))]
    if not scores:
        return None
    return round(sum(scores) / (len(scores) * 10) * 100)
