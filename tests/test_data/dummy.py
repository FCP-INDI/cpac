from cpac.api.schedules import Schedule, DataSettingsSchedule, DataConfigSchedule, ParticipantPipelineSchedule
from cpac.api.backends.base import Backend, BackendSchedule, RunStatus


class DataSplitterSchedule(Schedule):
    def __init__(self, data, parent=None):
        super().__init__(parent=parent)
        self.data = data

    def pre(self):
        self.pieces = self.data.split(' ')

    def post(self):
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

    @property
    def logs(self):
        return {
            'length': len(self['text/pieces'])
        }


class DummyDataUppererSchedule(DummySchedule, DataUppererSchedule):

    def run(self):
        self._results['text'] = self.data.upper()

    @property
    def status(self):
        if self.data.upper() == 'CRAZY':
            return RunStatus.FAILED
        return RunStatus.SUCCESS

    @property
    def logs(self):
        return {
            'length': len(self['text'])
        }


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
