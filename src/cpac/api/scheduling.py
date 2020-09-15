import os
import yaml
import sqlite3
import collections
import logging
import asyncio
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from appdirs import AppDirs

from .schedules import Schedule
from .backends.base import BackendSchedule

logger = logging.getLogger(__name__)


MAX_PARALLEL = 10
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

    events = [
        Schedule.Spawn,
        Schedule.Start,
        Schedule.End,
        BackendSchedule.Log,
        BackendSchedule.Status,
        BackendSchedule.Result,
    ]

    def __init__(self, backend, persistent=False, proxy=False):
        self.backend = backend(self)
        self.persistent = persistent
        self.proxy = proxy
        self._db_connection = None
        self._schedules = ScheduleTree(name='ROOT')
        self._futures = {}
        self._watchers = {c: {} for c in Scheduler.events}
        self._loop = asyncio.get_event_loop()
        self._semaphore = asyncio.Semaphore(MAX_PARALLEL)

    @property
    def config_dir(self):
        from cpac import __version__
        dirs = AppDirs(
            appname='cpac',
            appauthor=False,
            version=__version__
        )
        return dirs.user_config_dir

    @property
    def config_file(self):
        return os.path.join(self.config_dir, 'cpacpy.yml')

    @property
    def database_file(self):
        if not self._db_connection:
            return ':memory:'
        return os.path.join(self.config_dir, 'cpacpy.db')

    @property
    def database(self):
        if self._db_connection is None:
            self._db_connection = sqlite3.connect(self.database_file)
        return self._db_connection

    def load_config(self):
        with open(self.config_file, 'r') as f:
            self._config = yaml.safe_load(f)

    def save_config(self):
        with open(self.config_file, 'w') as f:
            yaml.dump(self._config, f)

    def __getitem__(self, key):
        return self._schedules.children[key if isinstance(key, str) else repr(str)]

    async def __aenter__(self):
        self.database
        return self

    def __await__(self):
        pending = self._futures.values()
        while not all(t.done() for t in pending):
            yield from asyncio.gather(*pending, loop=self._loop).__await__()
            yield from asyncio.sleep(2, loop=self._loop).__await__()
            pending = self._futures.values()

    async def __aexit__(self, exc_type, exc, tb):
        pass
        # if self._db_connection:
        #     self._db_connection.close()
        # self.save_config()

    def schedule(self, schedule, parent=None, name=None, proxied=False):

        if not proxied:
            backend = self.backend
            if isinstance(schedule, BackendSchedule):
                raise ValueError(f"Schedule must be naive, got {schedule.__class__.__name__}")

            schedule = backend.specialize(schedule)

        schedule_id = repr(schedule)
        self._schedules.children[schedule_id] = ScheduleTree(name=name, parent=parent, schedule=schedule)
        if parent:
            self._schedules[repr(parent)].children[schedule_id] = self._schedules[schedule_id]

        if not proxied:
            self._futures[schedule_id] = self._loop.create_task(
                self.run_scheduled(schedule)
            )

        return schedule

    def watch(self, schedule, function, children=False, watcher_classes=None):
        sid = repr(schedule)
        watcher_classes = watcher_classes or self.events
        logger.info(f"[Scheduler] Scheduling watcher on schedule {schedule} for watchers {[w.__name__ for w in watcher_classes]}")
        for watcher_class in watcher_classes:
            if sid not in self._watchers[watcher_class]:
                self._watchers[watcher_class][sid] = []
            self._watchers[watcher_class][sid] += [{
                "function": function,
                "children": children,
            }]

    def unwatch(self, schedule, function):
        sid = repr(schedule)
        logger.info(f"[Scheduler] Unscheduling watcher on schedule {schedule}")
        for watcher_class in self.events:
            if sid not in self._watchers[watcher_class]:
                continue
            try:
                self._watchers[watcher_class][sid].remove(function)
            except ValueError:
                pass

    async def run_scheduled(self, schedule):

        async with self._semaphore:

            it = schedule()
            sid = repr(schedule)

            async for message in it:

                watchers = self._watchers[message.__class__].get(sid, [])

                logger.info(f"[Scheduler] Got message {message.__class__.__name__} from schedule {schedule} ({len(watchers)})")

                if isinstance(message, Schedule.Spawn):

                    name = message.name
                    subschedule = message.child

                    logger.info(f'[Scheduler] Scheduling {subschedule} from {schedule}')

                    if not self.proxy:

                        for watcher_class in self._watchers:
                            for watcher in self._watchers[watcher_class].get(sid, []):
                                children = watcher["children"]
                                if not children:
                                    continue

                                self.watch(
                                    schedule=subschedule,
                                    function=watcher["function"],
                                    children=watcher["children"],
                                    watcher_classes=[watcher_class],
                                )

                    self.schedule(
                        subschedule,
                        parent=schedule,
                        name=name,
                        proxied=self.proxy
                    )

                for watcher in watchers:
                    function = watcher["function"]
                    try:
                        function(function, schedule, message)
                    except Exception as e:
                        logger.exception(e)

            for watcher_class in self._watchers:
                if sid in self._watchers[watcher_class]:
                    del self._watchers[watcher_class][sid]

            logger.info(f"[Scheduler] Schedule {schedule} is done ({await schedule.status})")

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
