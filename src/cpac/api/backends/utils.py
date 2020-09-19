import asyncio
import logging
import socket
import time
import uuid
from contextlib import closing
from subprocess import PIPE, STDOUT, Popen

logger = logging.getLogger(__name__)


def struuid(s, namespace):
    return str(uuid.uuid5(uuid.UUID(namespace) if namespace else uuid.UUID(int=0), s))


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
                    await cancel_tasks()
                    if isinstance(next_item, StopAsyncIteration):
                        break
                    raise next_item
                yield next_item
        finally:
            await cancel_tasks()

    async def cancel_tasks():
        try:
            nonlocal cancelling
            cancelling = True
            for t in tasks:
                t.cancel()

            while not all([t.done() for t in tasks]):
                await asyncio.sleep(0.1)
        except:
            pass

    tasks = [asyncio.create_task(drain(aiter)) for aiter in aiters]
    return merged(), tasks, cancel_tasks


def wait_for_port(address, timeout=5.0):
    host, port = address.split(':')
    start_time = time.perf_counter()
    while True:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                break
        except OSError as ex:
            time.sleep(0.01)
            if time.perf_counter() - start_time >= timeout:
                raise TimeoutError('Waited too long for the port {} on host {} to start accepting '
                                   'connections.'.format(port, host)) from ex


def process(command, cwd=None):
    return Popen(
        command,
        stdin=PIPE, stdout=PIPE, stderr=PIPE,
        cwd=cwd
    ).communicate(b"\n")