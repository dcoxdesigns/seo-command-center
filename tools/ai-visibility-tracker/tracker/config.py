"""Loads per-client tracker configs from clients/<name>/ai-visibility-tracker.json.

JSON instead of YAML deliberately — keeps this tool stdlib-only, no PyYAML
dependency, matching the rest of this repo's fetchers/ convention.
"""

import json
import os
from dataclasses import dataclass, field

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
CLIENTS_DIR = os.path.join(REPO_ROOT, "clients")
CONFIG_FILENAME = "ai-visibility-tracker.json"


@dataclass
class ClientConfig:
    slug: str  # the clients/<slug> directory name
    client: str
    domain: str
    brand_variants: list = field(default_factory=list)
    prompts: list = field(default_factory=list)

    @property
    def data_dir(self):
        d = os.path.join(CLIENTS_DIR, self.slug, "data", "ai-visibility-tracker")
        os.makedirs(d, exist_ok=True)
        return d


def load_client_config(slug):
    """Load a single client's config by their clients/ directory slug."""
    path = os.path.join(CLIENTS_DIR, slug, CONFIG_FILENAME)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return ClientConfig(
        slug=slug,
        client=raw["client"],
        domain=raw["domain"],
        brand_variants=raw.get("brand_variants", []),
        prompts=raw.get("prompts", []),
    )


def load_all_client_configs():
    """Load every client that has an ai-visibility-tracker.json — skips clients
    that don't (this tool is opt-in per client, not forced on the whole roster)
    and always skips _template."""
    configs = []
    if not os.path.isdir(CLIENTS_DIR):
        return configs
    for slug in sorted(os.listdir(CLIENTS_DIR)):
        if slug == "_template" or slug.startswith("."):
            continue
        if not os.path.isdir(os.path.join(CLIENTS_DIR, slug)):
            continue
        cfg = load_client_config(slug)
        if cfg is not None:
            configs.append(cfg)
    return configs
