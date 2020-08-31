import asyncio
import inspect
import logging
from collections.abc import Iterable
from dataclasses import dataclass

from ..schedules import (DataConfigSchedule, DataSettingsSchedule,
                         ParticipantPipelineSchedule, Schedule)

logger = logging.getLogger(__name__)


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

    @property
    async def status(self):
        raise NotImplementedError

    @property
    async def logs(self):
        return {}

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