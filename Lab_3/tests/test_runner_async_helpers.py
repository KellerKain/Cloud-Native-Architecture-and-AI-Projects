import asyncio

import pytest

from Lab_3.apps.runner import run_many, run_many_with_limit


@pytest.mark.asyncio
async def test_run_many_order_and_results():
    async def fn(s: str) -> str:
        await asyncio.sleep(0.01)
        return s.upper()

    prompts = ["a", "b", "c"]
    results = await run_many(fn, prompts)
    assert results == ["A", "B", "C"]


@pytest.mark.asyncio
async def test_run_many_with_limit_respects_limit():
    max_concurrent = 0
    current = 0
    lock = asyncio.Lock()

    async def fn(s: str) -> str:
        nonlocal max_concurrent, current
        async with lock:
            current += 1
            if current > max_concurrent:
                max_concurrent = current
        await asyncio.sleep(0.02)
        async with lock:
            current -= 1
        return s.upper()

    prompts = ["a", "b", "c", "d", "e"]
    results = await run_many_with_limit(fn, prompts, limit=2)
    assert results == [p.upper() for p in prompts]
    assert max_concurrent <= 2
