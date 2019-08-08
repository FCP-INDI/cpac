from theodore import __version__

import time
import yaml
import collections
from concurrent.futures import ThreadPoolExecutor   # `pip install futures` for python2



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
        return self.uid == self.other.uid

    @property
    def uid(self):
        raise NotImplementedError
        
    @property
    def status(self):
        raise NotImplementedError

    @property
    def logs(self):
        raise NotImplementedError


class Scheduler:

    def __init__(self, backends=[]):
        self._schedules = {
            None: {"children": {}, "parent": None, "schedule": None} # Root
        }
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

    def schedule(self, schedule, parent=None):
        assert isinstance(schedule, (Schedule, collections.Mapping))
        if isinstance(schedule, collections.Mapping):
            for sid, s in schedule.items():
                self._schedules[s] = {"children": {}, "parent": parent, "schedule": s}
                self._schedules[parent]["children"][sid] = self
                self.executor.submit(self.run_scheduled, s)
        else:
            self._schedules[schedule] = {"children": {}, "parent": parent, "schedule": schedule}
            self._schedules[parent]["children"][schedule.uid] = self._schedules[schedule]
            self.executor.submit(self.run_scheduled, schedule)

    def run_scheduled(self, schedule):
        try:
            for yid, y in schedule.run():
                if isinstance(y, Schedule):
                    self.schedule({
                        yid: y   
                    }, parent=schedule)
        except:
            import traceback
            traceback.print_exc()

    @property
    def statuses(self):
        statuses = {}
        # for _s in sorted(self._schedules, key=lambda x: 0 if x.parent is None else 1):
        #     statuses[_s.uid] = {"status": _s.status}
        #     if _s.parent:
        #         if "schedules" not in statuses[_s.parent.uid]:
        #             statuses[_s.parent.uid]["schedules"] = {}    
        #         statuses[_s.parent.uid]["schedules"][_s.uid] = statuses[_s.uid]

        return statuses

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
