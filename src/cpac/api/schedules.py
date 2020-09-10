import uuid
from ..utils import traverse_deep
from dataclasses import dataclass


class Schedule:

    def __init__(self, parent=None):
        self.parent = parent
        self._uid = str(uuid.uuid4())
        self._results = {}

    @dataclass
    class Spawn:
        schedule: 'Schedule'
        name: str
        child: 'Schedule'

    @dataclass
    class Start:
        schedule: 'Schedule'

    @dataclass
    class End:
        schedule: 'Schedule'
        status: str

    # TODO how to call all the supers from multiple inheritance
    async def pre(self):
        raise NotImplementedError

    # TODO how to call all the supers from multiple inheritance
    async def post(self):
        raise NotImplementedError

    def __hash__(self):
        return hash(self.uid)

    def __repr__(self):
        return self._uid

    def __str__(self):
        return f'{self.__class__.__name__}({self._uid})'

    def __eq__(self, other):
        return isinstance(other, (type(self), str)) and str(self) == str(other)

    def __getitem__(self, key):
        return self.result(key)

    def __getstate__(self):
        return self.__dict__

    def result(self, key):
        keys = key.split('/')
        try:
            return traverse_deep(self._results, keys)
        except KeyError as e:
            raise KeyError(*e.args)
    @property
    def base(self):
        return self.__class__

    @property
    def uid(self):
        return self._uid
        
    @property
    def available_results(self):
        return list(self._results.keys())

    @property
    def results(self):
        return self._results

    def __json__(self):
        raise NotImplementedError


class DataSettingsSchedule(Schedule):

    def __init__(self, data_settings, parent=None):
        super().__init__(parent=parent)
        self.data_settings = data_settings

    def __json__(self):
        return {
            "data_settings": self.data_settings,
        }


class DataConfigSchedule(Schedule):

    def __init__(self, data_config, pipeline=None, schedule_participants=True, parent=None):
        super().__init__(parent=parent)
        self.data_config = data_config
        self.pipeline = pipeline
        self.schedule_participants = schedule_participants

    def __json__(self):
        return {
            "data_config": self.data_config,
            "pipeline": self.pipeline,
            "schedule_participants": self.schedule_participants,
        }

    async def post(self):

        data_config = self['data_config']

        if self.schedule_participants:
            for subject in data_config:
                subject_id = []
                if 'site_id' in subject:
                    subject_id += [subject['site_id']]
                if 'subject_id' in subject:
                    subject_id += [subject['subject_id']]
                if 'unique_id' in subject:
                    subject_id += [subject['unique_id']]

                yield Schedule.Spawn(
                    schedule=self,
                    name='/'.join(subject_id),
                    child=ParticipantPipelineSchedule(pipeline=self.pipeline, subject=subject),
                )


class ParticipantPipelineSchedule(Schedule):

    def __init__(self, subject, pipeline=None, parent=None):
        super().__init__(parent=parent)
        self.subject = subject  # TODO rename to participant
        self.pipeline = pipeline

    def __json__(self):
        return {
            "subject": self.subject,
            "pipeline": self.pipeline,
        }

schedules = [
    Schedule,
    DataSettingsSchedule,
    DataConfigSchedule,
    ParticipantPipelineSchedule,
]