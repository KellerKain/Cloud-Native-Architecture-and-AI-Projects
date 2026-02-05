import asyncio
from typing import Awaitable, Callable, List

AsyncStrFn = Callable[[str], Awaitable[str]]


async def run_many(fn: AsyncStrFn, prompts: List[str]) -> List[str]:
	"""
	Run fn(prompt) concurrently for all prompts and return results in the same order.
	Requirements:
	- Use asyncio.gather
	- Do NOT run sequentially in a for-loop with await inside the loop
	"""
	tasks = [asyncio.create_task(fn(p)) for p in prompts]
	return await asyncio.gather(*tasks)


async def run_many_with_limit(fn: AsyncStrFn, prompts: List[str], limit: int) -> List[str]:
	"""
	Run fn(prompt) concurrently but limit the number of in-flight tasks to `limit`.
	Hint:
	- Use asyncio.Semaphore
	- Preserve output order
	"""
	if limit <= 0:
		raise ValueError("limit must be > 0")

	sem = asyncio.Semaphore(limit)

	async def _worker(prompt: str) -> str:
		async with sem:
			return await fn(prompt)

	tasks = [asyncio.create_task(_worker(p)) for p in prompts]
	return await asyncio.gather(*tasks)


if __name__ == "__main__":
	async def _demo_fn(s: str) -> str:
		await asyncio.sleep(0.01)
		return s.upper()

	async def _main():
		prompts = ["a", "b", "c", "d"]
		print(await run_many(_demo_fn, prompts))
		print(await run_many_with_limit(_demo_fn, prompts, limit=2))

	asyncio.run(_main())

