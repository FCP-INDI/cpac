import asyncio
import logging
import socket
from contextlib import closing

logger = logging.getLogger(__name__)


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


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

    async def cancel_tasks():
        nonlocal cancelling
        cancelling = True
        for t in tasks:
            t.cancel()

        while not all([t.done() for t in tasks]):
            await asyncio.sleep(0.1)

    tasks = [asyncio.create_task(drain(aiter)) for aiter in aiters]
    return merged(), tasks, cancel_tasks
