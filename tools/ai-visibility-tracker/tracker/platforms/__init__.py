"""Platform integrations. Each module exposes NAME, ENV_KEY, and call(prompt, api_key)."""

from . import chatgpt, gemini, perplexity

ALL = [chatgpt, perplexity, gemini]
BY_NAME = {p.NAME: p for p in ALL}
