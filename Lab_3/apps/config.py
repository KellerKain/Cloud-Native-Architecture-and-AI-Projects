"""Configuration for Lab_3 apps.

This module will attempt to load `Open_Router_Key` from a local
`openrouter_key.py` file (git-ignored) and fall back to the
`OPENROUTER_API_KEY` environment variable if the file is absent or empty.
"""
import os


def _load_local_key() -> str:
    try:
        import openrouter_key as _ok

        return getattr(_ok, "Open_Router_Key", "") or ""
    except Exception:
        return ""


API_KEY = _load_local_key() or os.getenv("OPENROUTER_API_KEY", "")

# OpenRouter endpoint and default model
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "mistralai/devstral-2512:free"

CONFIG = {
    "API_KEY": API_KEY,
    "OPENROUTER_URL": OPENROUTER_URL,
    "DEFAULT_MODEL": DEFAULT_MODEL,
    "TIMEOUT": 30,  # seconds
    "RETRY_COUNT": 3,
}

