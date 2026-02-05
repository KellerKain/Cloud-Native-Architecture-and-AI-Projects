import pytest
import httpx

import Lab_3.apps.openrouter_client as oc


class DummyResponse:
    def __init__(self, status_code: int, text: str = "", json_data=None):
        self.status_code = status_code
        self._text = text
        self._json = json_data

    def json(self):
        if self._json is None:
            raise ValueError("no json")
        return self._json

    @property
    def text(self):
        return self._text

    def raise_for_status(self):
        if 400 <= self.status_code < 600:
            raise httpx.HTTPStatusError("http", request=None, response=self)


class DummyClient:
    def __init__(self, timeout=None, responses=None):
        # copy responses list so factory can be reused
        self._responses = list(responses or [])

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, json, headers=None):
        if not self._responses:
            return DummyResponse(200, json_data={"output": "ok:" + json.get("input", "")})
        resp = self._responses.pop(0)
        if isinstance(resp, Exception):
            raise resp
        return resp


def make_client_factory(responses):
    def factory(timeout=None):
        return DummyClient(timeout=timeout, responses=responses)

    return factory


@pytest.mark.asyncio
async def test_generate_success(monkeypatch):
    monkeypatch.setattr(oc.httpx, "AsyncClient", make_client_factory([DummyResponse(200, json_data={"output": "hello"})]))
    client = oc.OpenRouterClient()
    out = await client.generate("prompt")
    assert out == "hello"


@pytest.mark.asyncio
async def test_generate_retries_on_5xx_then_succeeds(monkeypatch):
    monkeypatch.setattr(
        oc.httpx,
        "AsyncClient",
        make_client_factory([DummyResponse(500), DummyResponse(200, json_data={"output": "ok"})]),
    )
    client = oc.OpenRouterClient()
    out = await client.generate("p")
    assert out == "ok"


@pytest.mark.asyncio
async def test_generate_raises_on_4xx(monkeypatch):
    monkeypatch.setattr(oc.httpx, "AsyncClient", make_client_factory([DummyResponse(400)]))
    client = oc.OpenRouterClient()
    with pytest.raises(httpx.HTTPStatusError):
        await client.generate("p")


@pytest.mark.asyncio
async def test_generate_retries_on_timeout(monkeypatch):
    monkeypatch.setattr(
        oc.httpx,
        "AsyncClient",
        make_client_factory([httpx.ReadTimeout("t"), DummyResponse(200, json_data={"output": "ok"})]),
    )
    client = oc.OpenRouterClient()
    out = await client.generate("p")
    assert out == "ok"
