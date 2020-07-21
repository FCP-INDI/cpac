import time
import yaml
import collections
import logging
import asyncio
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor

from .schedules import Schedule
from .backends.base import BackendSchedule

logger = logging.getLogger(__name__)

SCHEDULER_ADDRESS = ('localhost', 3333)


class ScheduleTree:

    def __init__(self, name, schedule=None, children=None, parent=None):
        self.name = name
        self.children = children or {}
        self.parent = parent
        self.schedule = schedule

    @property
    async def status(self):
        return self.schedule.status
    
    @property
    async def logs(self):
        return self.schedule.logs

    def __getitem__(self, key):
        return self.children[key]
    
    def __setitem__(self, key, child):
        self.children[key] = child


class Scheduler:

    def __init__(self, backend):
        self.backend = backend(self)
        self._schedules = ScheduleTree(name='ROOT')
        self._futures = {}
        self._watchers = {
            Schedule.Spawn: {},
            BackendSchedule.Log: {},
        }

    def __getitem__(self, key):
        return self._schedules.children[key]

    async def __aenter__(self):
        self._loop = asyncio.get_event_loop()
        self._executor = ThreadPoolExecutor()
        return self

    def __await__(self):
        pending = self._futures.values()
        while not all(t.done() for t in pending):
            yield from asyncio.gather(*pending, loop=self._loop).__await__()
            yield from asyncio.sleep(2, loop=self._loop).__await__()
            pending = self._futures.values()

    async def __aexit__(self, exc_type, exc, tb):
        self._executor.shutdown(wait=True)

    def schedule(self, schedule, parent=None, name=None):

        backend = self.backend

        if isinstance(schedule, BackendSchedule):
            raise ValueError(f"Schedule must be naive, got {schedule.__class__.__name__}")

        schedule = backend.specialize(schedule)
        schedule_id = repr(schedule)

        self._schedules.children[schedule_id] = ScheduleTree(name=name, parent=parent, schedule=schedule)
        if parent:
            self._schedules[repr(parent)].children[schedule_id] = self._schedules[schedule_id]

        # self._futures[schedule_id] = self._loop.run_in_executor(
        #     self._executor,
        #     self.run_scheduled,
        #     schedule
        # )

        self._futures[schedule_id] = self._loop.create_task(
            self.run_scheduled(schedule)
        )

        return schedule

    def watch(self, schedule, function, children=False):
        schedule = str(schedule)
        if schedule not in self._watchers:
            self._watchers[schedule] = []
        self._watchers[schedule] += [{
            "function": function,
            "children": children,
        }]

    async def run_scheduled(self, schedule):

        it = schedule()
        sid = str(schedule)

        async for message in it:

            if isinstance(message, Schedule.Spawn):

                name = message.name
                subschedule = message.schedule

                logger.info(f'Scheduling {subschedule} from {schedule}')

                for watcher in self._watchers[Schedule.Spawn].get(sid, []):

                    children = watcher["children"]
                    if not children:
                        continue

                    self.watch(
                        schedule=subschedule,
                        function=watcher["function"],
                        children=watcher["children"],
                    )

                self.schedule(
                    subschedule,
                    parent=schedule,
                    name=name
                )


            for watcherclass in self._watchers:
                for watcher in self._watchers[watcherclass].get(sid, []):
                    function = watcher["function"]
                    try:
                        function(schedule, message)
                    except Exception as e:
                        print(e)

        for watcherclass in self._watchers:
            if sid in self._watchers[watcherclass]:
                for watcher in self._watchers[watcherclass][sid]:
                    function = watcher["function"]
                    try:
                        function(schedule)
                    except Exception as e:
                        print(e)
                del self._watchers[watcherclass][sid]

        return schedule


    @property
    async def statuses(self):
        root = self._schedules
        nodes = {}
        for schedule_id, child in root.children.items():
            schedule = child.schedule

            node = {}
            node["id"] = schedule_id
            node["status"] = await schedule.status
            if child.name:
                node['name'] = child.name
            if child.parent:
                node["parent"] = repr(child.parent)
            if child.children:
                node["children"] = [k for k in child.children.keys()]
            nodes[schedule_id] = node

        return nodes


    @property
    async def logs(self):
        root = self._schedules
        nodes = {}
        for schedule_id, child in root.children.items():
            schedule = child.schedule

            node = {}
            node["id"] = schedule_id
            node["logs"] = await schedule.logs
            if child.name:
                node['name'] = child.name
            if child.parent:
                node["parent"] = repr(child.parent)
            if child.children:
                node["children"] = [k for k in child.children.keys()]
            nodes[schedule_id] = node
        return nodes
