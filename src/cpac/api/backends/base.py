import logging
from collections.abc import Iterable
from ..schedules import Schedule, DataSettingsSchedule, DataConfigSchedule, ParticipantPipelineSchedule

logger = logging.getLogger(__name__)

class RunStatus:
    UNSTARTED = 'UNSTARTED'
    STARTING = 'STARTING'
    RUNNING = 'RUNNING'
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'
    UNKNOWN = 'UNKNOWN'


class Backend:

    base_schedule_class = None

    schedule_mapping = {
        Schedule: None,
        DataSettingsSchedule: None,
        DataConfigSchedule: None,
        ParticipantPipelineSchedule: None,
    }

    def __init__(self, scheduler):
        self.scheduler = scheduler

    def __getitem__(self, key):
        return self.schedule_mapping.get(key)


class BackendSchedule:

    _run = None

    def __init__(self, backend):
        self.backend = backend

    def __setstate__(self, state):
        self.__dict__.update(state)

    @property
    def status(self):
        raise NotImplementedError

    @property
    def logs(self):
        return {
            'id': repr(self),
            'hash': hash(self),
        }

    def __call__(self):
        
        if hasattr(self, 'pre_run'):
            try:
                logger.info(f'[{self}] Pre-running')
                it = self.pre_run()
                if isinstance(it, Iterable):
                    yield from it
            except NotImplementedError:
                pass

        logger.info(f'[{self}] Running')
        it = self.run()
        if isinstance(it, Iterable):
            yield from it

        if hasattr(self, 'post_run'):
            try:
                logger.info(f'[{self}] Post-running')
                it = self.post_run()
                if isinstance(it, Iterable):
                    yield from it
            except NotImplementedError:
                pass
            
    def run(self):
        pass