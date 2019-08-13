from theodore import __version__

import time
import yaml
import collections
from concurrent.futures import ThreadPoolExecutor   # `pip install futures` for python2
from collections.abc import Iterable


MAX_WORKERS = 1


class Schedule:

    def __init__(self, backend, parent=None):
        self.backend = backend
        self.parent = parent

    def run(self):
        raise NotImplementedError

    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other):
        return isinstance(other, (type(self), str)) and str(self) == str(other)

    @property
    def uid(self):
        raise NotImplementedError
        
    @property
    def status(self):
        raise NotImplementedError

    @property
    def logs(self):
        raise NotImplementedError


class ScheduleTree:
    def __init__(self, name, children=None, parent=None, schedule=None):
        self.name = name
        self.children = children or {}
        self.parent = parent
        self.schedule = schedule

    @property
    def status(self):
        status = {'children': {}}
        if self.schedule:
            status['status'] = self.schedule.status
        for k, v in self.children.items():
            status['children'][str(k)] = v.status
        return status


class Scheduler:

    def __init__(self, clients, clients_priority):
        self._schedules = ScheduleTree(name='ROOT')
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
        self.clients = {
            k: client_class(self)
            for k, client_class in clients.items()
        }
        self.clients_priority = clients_priority
        self._watchers = {}

    def __getitem__(self, key):
        return self._schedules.children[key]

    def schedule(self, schedule, parent=None, client=None):

        if client:
            assert client in self.clients
            client = self.clients[client]
        else:
            client = self.clients[self.clients_priority[0]]

        if isinstance(schedule, collections.Mapping):
            schedules = {}
            for sid, s in schedule.items():
                s = s(client)
                self._schedules[s] = ScheduleTree(name=sid, parent=parent, schedule=s)
                if parent:
                    self._schedules[parent]["children"][sid] = self
                    self._schedules[parent].children[sid] = self._schedules[s]
                schedules[sid] = s
                self.executor.submit(self.run_scheduled, s)
            return schedules
        else:
            schedule = schedule(client)
            self._schedules.children[schedule] = ScheduleTree(name=schedule.uid, parent=parent, schedule=schedule)
            if parent:
                self._schedules[parent].children[schedule] = self._schedules[schedule]
            self.executor.submit(self.run_scheduled, schedule)
            return schedule

    def watch(self, schedule, function, children=False):
        schedule = str(schedule)
        if schedule not in self._watchers:
            self._watchers[schedule] = []
        self._watchers[schedule] += [{
            "function": function,
            "children": children,
        }]

    def run_scheduled(self, schedule):
        try:
            it = schedule.run()
            sid = str(schedule)

            if isinstance(it, Iterable):
                for yid, y in it:
                    if not isinstance(y, Schedule):
                        continue

                    self.schedule({
                        yid: y   
                    }, parent=schedule)

                    if sid in self._watchers:
                        for watcher in self._watchers[sid]:
                            children = watcher["children"]
                            if not children:
                                continue

                            self.watch(
                                schedule=y,
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
        except:
            import traceback
            traceback.print_exc()

    @property
    def statuses(self):
        return self._schedules.status

    @property
    def logs(self):

        def __transverse_logs(root):
            node = {}
            if root["schedule"]:
                node["logs"] = root["schedule"].logs
            node["children"] = {}
            for id, s in root["children"].items():
                node["children"][id] = __transverse_logs(s)
            return node

        # for _s in sorted(self._schedules, key=lambda x: 0 if x.parent is None else 1):
        #     logs[_s.uid] = {"logs": _s.logs}
        #     if _s.parent:
        #         if "schedules" not in logs[_s.parent.uid]:
        #             logs[_s.parent.uid]["schedules"] = {}    
        #         logs[_s.parent.uid]["schedules"][_s.uid] = logs[_s.uid]

        return __transverse_logs(self._schedules[None])
