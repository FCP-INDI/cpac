import asyncio
import logging

logger = logging.getLogger(__name__)


async def consume(async_gen):
    items = []
    async for item in async_gen:
        items += [item]
    return items


def merge_async_iters(*aiters):
    queue = asyncio.Queue(1)
    start_run_count = len(aiters)
    run_count = len(aiters)
    cancelling = False

    async def drain(aiter):
        nonlocal run_count
        try:
            async for item in aiter:
                await queue.put((False, item))
        except Exception as e:
            if not cancelling:
                await queue.put((True, e))
            else:
                raise
        finally:
            run_count -= 1

    async def merged():
        try:
            while run_count == start_run_count:
                raised, next_item = await queue.get()
                if next_item is None:
                    continue
                if raised:
                    cancel_tasks()
                    if isinstance(next_item, StopAsyncIteration):
                        break
                    raise next_item
                yield next_item
        finally:
            cancel_tasks()

    def cancel_tasks():
        nonlocal cancelling
        cancelling = True
        for t in tasks:
            t.cancel()

    tasks = [asyncio.create_task(drain(aiter)) for aiter in aiters]
    return merged()