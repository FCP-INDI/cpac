import os
import time
import glob
import yaml
import docker
import shutil
import tempfile
import hashlib
import uuid
import copy

from base64 import b64decode, b64encode

from ..utils import string_types
from ..scheduler import Schedule, SubSchedule
from .backend import Backend

from tornado import httpclient


class Docker(Backend):

    tag = 'latest'

    def __init__(self, scheduler):
        self.client = docker.from_env()
        try:
            self.client.ping()
        except docker.errors.APIError:
            raise "Could not connect to Docker"
        self.scheduler = scheduler

    def schedule(self, pipeline_config, data_config):
        self.scheduler.schedule(DockerSchedule(self, pipeline_config, data_config))


class DockerRun(object):

    def __init__(self, container):
        self.container = container
        print(container)

    @property
    def status(self):
        try:
            self.container.reload()
        except Exception as e:
            return 'stopped'
        status = self.container.status
        status_map = {
            'created': 'starting', 
            'restarting': 'running', 
            'running': 'running', 
            'removing': 'running', 
            'paused': 'running', 
            'exited': 'success', 
            'dead': 'failed'
        }
        if status in status_map:
            return status_map[status]

        return 'unknown'


class DockerSchedule(Schedule):

    def __init__(self, backend, pipeline_config=None, data_config=None, parent=None):
        super(DockerSchedule, self).__init__(backend=backend, parent=parent)
        self.pipeline_config = pipeline_config
        self.data_config = data_config
        self._uid = str(uuid.uuid4())

    @property
    def uid(self):
        return self._uid

    @property
    def logs(self):
        return [{
            'id': 'schedule',
            'hash': 'schedule',
        }]

    def run(self):
        if self.data_config:
            yield (
                'data_config',
                DockerDataConfigSchedule(
                    self.backend,
                    self.pipeline_config,
                    self.data_config,
                    parent=self
                )
            )


class DockerSubjectSchedule(DockerSchedule):

    def __init__(self, backend, pipeline_config, subject, parent=None):
        super(DockerSubjectSchedule, self).__init__(backend=backend, parent=parent)
        self.pipeline_config = pipeline_config
        self.subject = subject
        self._run = None

    @staticmethod
    def _remap_files(subject):
        mapping = {}
        subject = copy.deepcopy(subject)

        if isinstance(subject, string_types):
            if '/' not in subject:
                return subject, mapping

            if subject.startswith('s3://'):
                return subject, mapping
            else:
                subject = os.path.abspath(os.path.realpath(subject))
                md5 = hashlib.md5()
                md5.update(os.path.dirname(subject).encode())
                mapping[os.path.dirname(subject)] = '/' + md5.hexdigest()
                return '/' + md5.hexdigest() + '/' + os.path.basename(subject), mapping

        elif isinstance(subject, dict):
            for key, val in subject.items():
                subject[key], submapping = DockerSubjectSchedule._remap_files(val)
                mapping.update(submapping)
            return subject, mapping

        elif isinstance(subject, list):
            for key, val in enumerate(subject):
                subject[key], submapping = DockerSubjectSchedule._remap_files(val)
                mapping.update(submapping)
            return subject, mapping

    def run(self):
        config_folder = tempfile.mkdtemp()
        output_folder = tempfile.mkdtemp()

        if self.pipeline_config is not None:
            new_pipeline_config = os.path.join(config_folder, 'pipeline.yml')
            shutil.copy(self.pipeline_config, new_pipeline_config)
            pipeline_config = new_pipeline_config

        volumes = {
            '/tmp': {'bind': '/scratch', 'mode': 'rw'},
            config_folder: {'bind': '/config', 'mode':'ro'},
            output_folder: {'bind': '/output', 'mode':'rw'},
        }

        subject = 'data:text/plain;base64,' + \
            b64encode(yaml.dump([self.subject], default_flow_style=False).encode("utf-8")).decode("utf-8")

        # TODO handle local databases, transverse subject dict to get folder mappings
        command = ['/', '/output', 'participant',
                '--monitoring',
                '--data_config_file', subject]

        if self.pipeline_config:
            command += ['--pipeline_file', '/config/pipeline.yml']

        self._run = DockerRun(self.backend.client.containers.run(
            'fcpindi/c-pac:' + self.backend.tag,
            command=command,
            detach=True,
            ports={'8080/tcp': None},
            volumes=volumes,
            working_dir='/pwd'
        ))

        self._run.container.wait()

    @property
    def status(self):
        if not self._run:
            return "unstarted"
        else:
            return self._run.status

    @property
    def logs(self):

        if not self._run:
            return []

        try:
            self._run.container.reload()
        except Exception as e:
            return []

        if '8080/tcp' not in self._run.container.attrs['NetworkSettings']['Ports']:
            return []

        port = int(self._run.container.attrs['NetworkSettings']['Ports']['8080/tcp'][0]['HostPort'])

        http_client = httpclient.HTTPClient()

        try:
            response = json.loads(http_client.fetch("http://localhost:%d/" % port).body.decode('utf-8'))
        except Exception as e:
            print(e)
        http_client.close()

        return []

        
class DockerDataConfigSchedule(DockerSchedule):

    _start = None
    _finish = None

    def __init__(self, backend, pipeline_config, data_config, parent=None):
        super(DockerDataConfigSchedule, self).__init__(backend=backend, parent=parent)
        self.pipeline_config = pipeline_config
        self.data_config = data_config
        self._run = None

    def run(self):

        self._start = time.time()

        self._output_folder = tempfile.mkdtemp()
        
        volumes = {
            self._output_folder: {'bind': '/output_folder', 'mode': 'rw'},
            '/tmp': {'bind': '/scratch', 'mode': 'rw'},
        }

        data_config = None
        data_folder = '/'
        if "\n" in self.data_config:
            data_config = self.data_config
        else:
            data_folder = self.data_config

        if data_folder and not data_folder.startswith('s3://'):
            volumes[data_folder] = {'bind': '/data_folder', 'mode': 'ro'}
            data_folder = '/data_folder'

        container_args = [data_folder, '/output_folder', 'test_config']
        if data_config:
            if data_config.lower().startswith('data:'):
                container_args += ['--data_config_file', data_config]
            else:
                container_args += ['--data_config_file', os.path.basename(data_config)]
                volumes[os.path.dirname(data_config)] = {'bind': '/data_config_file', 'mode': 'ro'}

        self._run = DockerRun(self.backend.client.containers.run(
            'fcpindi/c-pac:' + self.backend.tag,
            command=container_args,
            detach=True,
            volumes=volumes
        ))

        self._run.container.wait()

        try:
            files = glob.glob(os.path.join(self._output_folder, 'cpac_data_config_*.yml'))
            if files:
                with open(files[0]) as f:
                    for subject in yaml.load(f):
                        subject_id = []
                        if 'site_id' in subject:
                            subject_id += [subject['site_id']]
                        if 'subject_id' in subject:
                            subject_id += [subject['subject_id']]
                        if 'unique_id' in subject:
                            subject_id += [subject['unique_id']]

                        yield (
                            '_'.join(subject_id),
                            DockerSubjectSchedule(self.backend, self.pipeline_config, subject, parent=self)
                        )
        finally:
            shutil.rmtree(self._output_folder)

        self._finish = time.time()

    @property
    def status(self):
        if not self._run:
            return "unstarted"
        else:
            return self._run.status

    @property
    def logs(self):
        log = {
            'id': 'data_config',
            'hash': 'data_config',
        }

        if self._start is not None:
            log['start'] = self._start

        if self._finish is not None:
            log['finish'] = self._finish

        return [log]
