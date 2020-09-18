import asyncio
import inspect
import io
import os
import json
import logging
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from ...utils import read_crash
from ..schedules import (DataConfigSchedule, DataSettingsSchedule,
                         ParticipantPipelineSchedule, Schedule)

logger = logging.getLogger(__name__)

class Result:
    _mime = 'application/json'

    @property
    def mime(self):
        return self._mime

class FileResult(Result):
    def __init__(self, path, mime=None, name=None):
        self._path = path
        self._mime = mime or 'text/plain'
        self._name = name or path

    async def __aenter__(self):
        self._stream = open(self._path)
        return self._stream

    async def __aexit__(self, exc_type, exc, tb):
        self._stream.close()

    @property
    def name(self):
        return self._name

    @property
    def size(self):
        pos = self._stream.tell()
        self._stream.seek(0, os.SEEK_END)
        size = self._stream.tell()
        self._stream.seek(pos)
        return size

    async def slice(
        self, start: int = None, end: int = None
    ):
        f = self._stream
        if start is not None:
            f.seek(start)
        if end is not None:
            remaining = end - (start or 0)
        else:
            remaining = None
        while True:
            chunk_size = 64 * 1024
            if remaining is not None and remaining < chunk_size:
                chunk_size = remaining
            chunk = f.read(chunk_size)
            if chunk:
                if remaining is not None:
                    remaining -= len(chunk)
                yield chunk
            else:
                if remaining is not None:
                    assert remaining == 0
                return


class LogFileResult(FileResult):
    def __init__(self, path, name=None):
        super().__init__(
            path,
            mime='application/vdn.cpacpy-log+json',
            name=name
        )


class CrashInputEncoder(json.JSONEncoder):
    def default(self, o):
        if o.__class__.__name__ == '_Undefined':
            return None
        try:
            return super().default(o)
        except TypeError:
            return f'{o}'


class CrashFileResult(FileResult):
    def __init__(self, path, name=None):
        super().__init__(
            path,
            mime='application/vdn.cpacpy-crash+json',
            name=name
        )

    async def __aenter__(self):
        self._stream = io.StringIO()
        data = read_crash(self._path)
        self._stream = io.StringIO()
        json.dump(data, self._stream, cls=CrashInputEncoder)
        self._stream.seek(0)
        return self._stream


class RunStatus:
    UNSTARTED = 'unstarted'
    RUNNING = 'running'
    SUCCESS = 'success'
    FAILURE = 'failure'
    UNKNOWN = 'unknown'

    finished = [SUCCESS, FAILURE]


class Backend:

    base_schedule_class = None

    schedule_mapping = {
        Schedule: None,
        DataSettingsSchedule: None,
        DataConfigSchedule: None,
        ParticipantPipelineSchedule: None,
    }

    def __init__(self, scheduler=None):
        self.scheduler = scheduler

    def __getitem__(self, key):
        return self.schedule_mapping.get(key)

    def __call__(self, scheduler):
        self.scheduler = scheduler
        return self

    def specialize(self, schedule):
        if self[schedule.__class__] is None:
            raise ValueError(f"Mapped scheduled class for {schedule.__class__.__name__} does not exist.")

        backend_schedule = self[schedule.__class__](backend=self)
        backend_schedule.__setstate__(schedule.__getstate__())
        return backend_schedule


class BackendSchedule:

    def __init__(self, backend):
        self.backend = backend

    def __setstate__(self, state):
        self.__dict__.update(state)

    @dataclass
    class Log:
        schedule: Schedule
        timestamp: float
        content: dict

    @dataclass
    class Status:
        schedule: Schedule
        timestamp: float
        status: str

    @dataclass
    class Result:
        schedule: Schedule
        result: Any
        timestamp: float
        key: str

    @property
    async def status(self):
        raise NotImplementedError

    @property
    async def logs(self):
        return {}

    @property
    def base(self):
        classes = [DataSettingsSchedule, ParticipantPipelineSchedule, DataConfigSchedule]
        return [
            c for c in classes
            if isinstance(self, c)
        ][0]

    async def run(self):
        raise NotImplementedError

    def __await__(self):
        while self.status not in self.finished:
            yield from asyncio.sleep(0.5).__await__()

    async def __call__(self):

        yield Schedule.Start(schedule=self)

        if hasattr(self, 'pre'):
            try:
                pre = self.pre()
                logger.info(f'[{self}] Pre-running')
                if inspect.isasyncgen(pre):
                    async for i in pre:
                        yield i
                else:
                    await pre
            except NotImplementedError:
                pass

        run = self.run()
        logger.info(f'[{self}] Running')
        if inspect.isasyncgen(run):
            async for i in run:
                yield i
        else:
            await run

        if hasattr(self, 'post'):
            try:
                post = self.post()
                logger.info(f'[{self}] Post-running')
                if inspect.isasyncgen(post):
                    async for i in post:
                        yield i
                else:
                    await post
            except NotImplementedError:
                pass
        
        yield Schedule.End(schedule=self, status=self._status)
