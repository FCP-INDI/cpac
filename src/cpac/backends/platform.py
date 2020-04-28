import os
import pwd
import tempfile


class Backend(object):

    def __init__(self):
        pass

    def start(self, pipeline_config, subject_config):
        raise NotImplementedError()

    def _set_bindings(self, **kwargs):
        tag = kwargs.get('tag', None)
        tag = tag if isinstance(tag, str) else 'latest'

        temp_dir = kwargs.get(
            'temp_dir',
            tempfile.mkdtemp(prefix='cpac_pip_temp_')
        )
        output_dir = kwargs.get(
            'output_dir',
            tempfile.mkdtemp(prefix='cpac_pip_output_')
        )
        working_dir = kwargs.get(
            'working_dir',
            os.getcwd()
        )

        self._bind_volume(temp_dir, temp_dir, 'rw')
        self._bind_volume(output_dir, output_dir, 'rw')
        self._bind_volume(working_dir, working_dir, 'rw')

        uid = os.getuid()

        self.bindings = {
            'gid': pwd.getpwuid(uid).pw_gid,
            'mounts': [
                '{}:{}:{}'.format(
                    i,
                    j['bind'],
                    j['mode']
                ) for i in self.volumes.keys() for j in self.volumes[i]
            ],
            'tag': tag,
            'uid': uid,
            'volumes': self.volumes
        }


class Result(object):

    mime = None

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __call__(self):
        yield self.value

    @property
    def description(self):
        return {
            'type': 'object'
        }


class FileResult(Result):

    def __init__(self, name, value, mime):
        self.name = name
        self.value = value
        self.mime = mime

    def __call__(self):
        with open(self.value, 'rb') as f:
            while True:
                piece = f.read(1024)
                if piece:
                    yield piece
                else:
                    return

    @property
    def description(self):
        return {
            'type': 'file',
            'mime': self.mime
        }
