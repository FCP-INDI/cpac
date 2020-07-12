import uuid
from ..utils import traverse_deep


class Schedule:

    def __init__(self, parent=None):
        self.parent = parent
        self._uid = str(uuid.uuid4())
        self._results = {}

    def pre(self):
        raise NotImplementedError

    def post(self):
        raise NotImplementedError

    def __hash__(self):
        return hash(self.uid)

    def __repr__(self):
        return self._uid

    def __str__(self):
        return f'{self.__class__.__name__}({self._uid})'

    def __eq__(self, other):
        return isinstance(other, (type(self), str)) and str(self) == str(other)

    def result(self, key):
        keys = key.split('/')
        return traverse_deep(self._results, keys)

    def __getitem__(self, key):
        return self.result(key)

    def __getstate__(self):
        return self.__dict__

    @property
    def uid(self):
        return self._uid
        
    @property
    def available_results(self):
        return list(self._results.keys())

    @property
    def results(self):
        return self._results


class DataSettingsSchedule(Schedule):

    def __init__(self, data_settings, parent=None):
        super().__init__(parent=parent)
        self.data_settings = data_settings


class DataConfigSchedule(Schedule):

    def __init__(self, data_config, pipeline=None, parent=None):
        super().__init__(parent=parent)
        self.data_config = data_config
        self.pipeline = pipeline

    def post(self):

        data_config = self['data_config']

        for subject in data_config:
            subject_id = []
            if 'site_id' in subject:
                subject_id += [subject['site_id']]
            if 'subject_id' in subject:
                subject_id += [subject['subject_id']]
            if 'unique_id' in subject:
                subject_id += [subject['unique_id']]

            yield (
                '/'.join(subject_id),
                ParticipantPipelineSchedule,
                {
                    'pipeline': self.pipeline,
                    'subject': subject,
                }
            )


class ParticipantPipelineSchedule(Schedule):

    def __init__(self, subject, pipeline=None, parent=None):
        super().__init__(parent=parent)
        self.subject = subject
        self.pipeline = pipeline
