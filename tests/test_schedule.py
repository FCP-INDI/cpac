import os
from cpac.api.scheduling import Scheduler
from cpac.api.schedules import Schedule, DataSettingsSchedule, DataConfigSchedule, ParticipantPipelineSchedule
from cpac.api.backends.base import Backend, BackendSchedule, RunStatus
from concurrent.futures import ThreadPoolExecutor


class DataSplitterSchedule(Schedule):
    def __init__(self, data, parent=None):
        super().__init__(parent=parent)
        self.data = data

    def pre_run(self):
        self.pieces = self.data.split(' ')

    def post_run(self):
        for piece in self['text/pieces']:
            yield (
                piece,
                DataUppererSchedule(data=piece)
            )

class DataUppererSchedule(Schedule):
    def __init__(self, data, parent=None):
        super().__init__(parent=parent)
        self.data = data


class DummySchedule(BackendSchedule):
    pass


class DummyDataSplitterSchedule(DummySchedule, DataSplitterSchedule):

    def run(self):
        self._results['text'] = {
            'pieces': self.pieces
        }
    
    @property
    def status(self):
        return RunStatus.SUCCESS


class DummyDataUppererSchedule(DummySchedule, DataUppererSchedule):

    def run(self):
        self._results['text'] = self.data.upper()

    @property
    def status(self):
        return RunStatus.SUCCESS


class DummyBackend(Backend):
    base_schedule_class = DummySchedule
    schedule_mapping = {
        Schedule: DummySchedule,
        DataSplitterSchedule: DummyDataSplitterSchedule,
        DataUppererSchedule: DummyDataUppererSchedule,
    }


class DummyExecutor:
    def __init__(self, *args, **kwargs):
        pass
    def submit(self, fn, param):
        fn(param)


def test_schedule(monkeypatch):

    scheduler = Scheduler(DummyBackend, executor=DummyExecutor)

    schedule = scheduler.schedule(
        DataSplitterSchedule(
            data="My crRazY dATa"
        )
    )

    print(scheduler[schedule].schedule)

    from pprint import pprint
    pprint(scheduler.statuses)
