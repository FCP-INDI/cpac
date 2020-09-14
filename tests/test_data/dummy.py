from cpac.api.schedules import Schedule, DataSettingsSchedule, DataConfigSchedule, ParticipantPipelineSchedule
from cpac.api.backends.base import Backend, BackendSchedule, RunStatus


class DataSplitterSchedule(Schedule):
    def __init__(self, data, parent=None):
        super().__init__(parent=parent)
        self.data = data

    async def pre(self):
        self.pieces = self.data.split(' ')

    async def post(self):
        for piece in self['text/pieces']:
            yield Schedule.Spawn(
                name=piece,
                schedule=self,
                child=DataUppererSchedule(data=piece)
            )


class DataUppererSchedule(Schedule):
    def __init__(self, data, parent=None):
        super().__init__(parent=parent)
        self.data = data


class DummySchedule(BackendSchedule):
    pass


class DummyDataSplitterSchedule(DummySchedule, DataSplitterSchedule):

    async def run(self):
        self._results['text'] = {
            'pieces': self.pieces
        }
        self._status = RunStatus.SUCCESS

    @property
    async def status(self):
        return RunStatus.SUCCESS

    @property
    async def logs(self):
        return {
            'length': len(self['text/pieces'])
        }


class DummyDataUppererSchedule(DummySchedule, DataUppererSchedule):

    async def run(self):
        self._results['text'] = self.data.upper()
        self._status = RunStatus.SUCCESS

    @property
    async def status(self):
        if self.data.upper() == 'CRAZY':
            return RunStatus.FAILURE
        return RunStatus.SUCCESS

    @property
    async def logs(self):
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
