"""Async OpenRouter client with timeout and retry behaviour.

This module will try to import configuration and an async retry helper
from `app.config` and `app.retry`. If those aren't available it will
fall back to reasonable defaults.
"""
import asyncio
from typing import Any

import httpx

# Try importing settings and retry helper from expected package locations
try:
    from app.config import OPENROUTER_API_KEY, OPENROUTER_URL, DEFAULT_MODEL
except Exception:
    try:
        from .config import CONFIG as _CONFIG

        OPENROUTER_API_KEY = _CONFIG.get("API_KEY", "")
        OPENROUTER_URL = _CONFIG.get("OPENROUTER_URL", "https://api.openrouter.ai/v1")
        DEFAULT_MODEL = _CONFIG.get("DEFAULT_MODEL", "gpt-4o-mini")
    except Exception:
        OPENROUTER_API_KEY = ""
        OPENROUTER_URL = "https://api.openrouter.ai/v1"
        DEFAULT_MODEL = "gpt-4o-mini"

try:
    from app.retry import retry_async  # type: ignore
except Exception:
    retry_async = None


def _make_retry_decorator(attempts: int = 3, delay: float = 1.0):
    """Return an async retry decorator used as a fallback when `retry_async` is missing."""

    def decorator(fn):
        async def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(attempts):
                try:
                    return await fn(*args, **kwargs)
                except httpx.HTTPStatusError as e:
                    status = e.response.status_code if e.response is not None else None
                    if status == 429 or (status is not None and 500 <= status < 600):
                        last_exc = e
                        await asyncio.sleep(delay)
                        continue
                    raise
                except (httpx.ReadTimeout, httpx.ConnectError, httpx.TransportError) as e:
                    last_exc = e
                    await asyncio.sleep(delay)
                    continue
            raise last_exc

        return wrapper

    return decorator


class OpenRouterClient:
    def __init__(self, model: str = DEFAULT_MODEL, timeout_s: float = 15.0) -> None:
        self.model = model
        self.timeout_s = timeout_s

    async def _call_api(self, prompt: str) -> str:
        headers = {}
        if OPENROUTER_API_KEY:
            headers["Authorization"] = f"Bearer {OPENROUTER_API_KEY}"

        timeout = httpx.Timeout(self.timeout_s)
        async with httpx.AsyncClient(timeout=timeout) as client:
            # Post a minimal payload; adapter users may change this shape
            resp = await client.post(OPENROUTER_URL, json={"model": self.model, "input": prompt}, headers=headers)

            # Retryable statuses: 429 and 5xx
            if resp.status_code == 429 or 500 <= resp.status_code < 600:
                # raise HTTPStatusError so retry decorators can catch it
                resp.raise_for_status()

            # For other 4xx errors, do NOT retry; raise to caller
            if 400 <= resp.status_code < 500:
                resp.raise_for_status()

            # Return best-effort string from JSON or raw text
            try:
                data = resp.json()
                # Common shapes: {'output': '...'} or {'choices': [{'text': '...'}]}
                if isinstance(data, dict):
                    if "output" in data:
                        return data["output"]
                    if "text" in data:
                        return data["text"]
                    if "choices" in data and isinstance(data["choices"], list) and data["choices"]:
                        first = data["choices"][0]
                        if isinstance(first, dict) and "text" in first:
                            return first["text"]
                return resp.text
            except Exception:
                return resp.text

    async def generate(self, prompt: str) -> str:
        """
        Requirements:
        - Use httpx.AsyncClient
        - Apply timeout
        - Retry on timeouts, transport errors, HTTP 429 and 5xx
        - Do NOT retry on other 4xx errors
        """
        attempts = 3
        delay = 1.0

        timeout = httpx.Timeout(self.timeout_s)
        async with httpx.AsyncClient(timeout=timeout) as client:
            for attempt in range(attempts):
                try:
                    resp = await client.post(OPENROUTER_URL, json={"model": self.model, "input": prompt}, headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"} if OPENROUTER_API_KEY else None)

                    # Retryable statuses: 429 and 5xx
                    if resp.status_code == 429 or 500 <= resp.status_code < 600:
                        # retryable server error: sleep and retry unless last attempt
                        if attempt == attempts - 1:
                            resp.raise_for_status()
                        await asyncio.sleep(delay)
                        continue

                    # For other 4xx errors, do NOT retry; raise to caller
                    if 400 <= resp.status_code < 500:
                        resp.raise_for_status()

                    # Return best-effort string from JSON or raw text
                    try:
                        data = resp.json()
                        if isinstance(data, dict):
                            if "output" in data:
                                return data["output"]
                            if "text" in data:
                                return data["text"]
                            if "choices" in data and isinstance(data["choices"], list) and data["choices"]:
                                first = data["choices"][0]
                                if isinstance(first, dict) and "text" in first:
                                    return first["text"]
                        return resp.text
                    except Exception:
                        return resp.text

                except httpx.HTTPStatusError as e:
                    status = e.response.status_code if e.response is not None else None
                    if status == 429 or (status is not None and 500 <= status < 600):
                        if attempt == attempts - 1:
                            raise
                        await asyncio.sleep(delay)
                        continue
                    # Non-retryable HTTP error
                    raise
                except (httpx.ReadTimeout, httpx.ConnectError, httpx.TransportError) as e:
                    if attempt == attempts - 1:
                        raise
                    await asyncio.sleep(delay)
                    continue

