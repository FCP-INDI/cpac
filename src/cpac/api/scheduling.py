import time
import yaml
import collections
import logging
from concurrent.futures import ThreadPoolExecutor
from collections.abc import Iterable

from .schedules import Schedule
from .backends.base import BackendSchedule

logger = logging.getLogger(__name__)

MAX_WORKERS = 1
SCHEDULER_ADDRESS = ('localhost', 3333)


class ScheduleTree:

    def __init__(self, name, schedule=None, children=None, parent=None):
        self.name = name
        self.children = children or {}
        self.parent = parent
        self.schedule = schedule

    @property
    def status(self):
        return self.schedule.status
    
    @property
    def logs(self):
        return self.schedule.logs

    def __getitem__(self, key):
        return self.children[key]
    
    def __setitem__(self, key, child):
        self.children[key] = child


class Scheduler:

    def __init__(self, backend, executor=ThreadPoolExecutor):
        self._schedules = ScheduleTree(name='ROOT')
        self.executor = executor(max_workers=MAX_WORKERS)
        self.backend = backend(self)
        self._watchers = {}

    def __getitem__(self, key):
        return self._schedules.children[key]

    def schedule(self, schedule, parent=None, name=None):

        backend = self.backend

        if isinstance(schedule, BackendSchedule):
            raise ValueError(f"Schedule must be naive, got {schedule.__class__.__name__}")

        schedule = self._mix_up(backend, schedule)

        self._schedules.children[schedule] = ScheduleTree(name=name, parent=parent, schedule=schedule)
        if parent:
            self._schedules[parent].children[schedule] = self._schedules[schedule]

        self.executor.submit(self.run_scheduled, schedule)

        return schedule

    def _mix_up(self, backend, schedule):

        if backend[schedule.__class__] is None:
            raise ValueError(f"Mapped scheduled class for {schedule.__class__.__name__} is None. {backend.schedule_mapping}")

        backend_schedule = backend[schedule.__class__](backend=backend)
        backend_schedule.__setstate__(schedule.__getstate__())

        return backend_schedule

    def watch(self, schedule, function, children=False):
        schedule = str(schedule)
        if schedule not in self._watchers:
            self._watchers[schedule] = []
        self._watchers[schedule] += [{
            "function": function,
            "children": children,
        }]

    def run_scheduled(self, schedule):

        it = schedule()
        sid = str(schedule)

        if isinstance(it, Iterable):
            for name, subschedule in it:

                if not isinstance(subschedule, Schedule):
                    logger.info(f'Not subclass')
                    continue

                logger.info(f'Scheduling {subschedule} from {schedule}')

                self.schedule(
                    subschedule,
                    parent=schedule,
                    name=name
                )

                if sid in self._watchers:
                    for watcher in self._watchers[sid]:
                        children = watcher["children"]
                        if not children:
                            continue

                        self.watch(
                            schedule=subschedule,
                            function=watcher["function"],
                            children=watcher["children"],
                        )

        if sid in self._watchers:
            for watcher in self._watchers[sid]:
                function = watcher["function"]

                try:
                    function(schedule)
                except Exception as e:
                    print(e)

            del self._watchers[sid]

    @property
    def statuses(self):
        root = self._schedules
        nodes = {}
        for schedule, child in root.children.items():
            node = {}
            node["id"] = repr(schedule)
            node["status"] = schedule.status
            if child.name:
                node['name'] = child.name
            if child.parent:
                node["parent"] = repr(child.parent)
            if child.children:
                node["children"] = [repr(k) for k in child.children.keys()]
            nodes[repr(schedule)] = node
        return nodes

    @property
    def logs(self):
        root = self._schedules
        nodes = {}
        for schedule, child in root.children.items():
            node = {}
            node["id"] = repr(schedule)
            node["logs"] = schedule.logs
            if child.name:
                node['name'] = child.name
            if child.parent:
                node["parent"] = repr(child.parent)
            if child.children:
                node["children"] = [repr(k) for k in child.children.keys()]
            nodes[repr(schedule)] = node
        return nodes
