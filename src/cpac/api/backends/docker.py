import copy
import glob
import hashlib
import json
import os
import shutil
import tempfile
import time
from base64 import b64decode, b64encode

import yaml
from tornado import httpclient

import docker

from .base import Backend, RunStatus, BackendSchedule
from ..schedules import Schedule, DataSettingsSchedule, DataConfigSchedule, ParticipantPipelineSchedule

class DockerRun(object):

    def __init__(self, container):
        self.container = container

    @property
    def status(self):
        try:
            self.container.reload()
        except Exception:
            return RunStatus.UNKNOWN

        status = self.container.status
        status_map = {
            'created': RunStatus.STARTING,
            'restarting': RunStatus.RUNNING,
            'running': RunStatus.RUNNING,
            'removing': RunStatus.RUNNING,
            'paused': RunStatus.RUNNING,
            'exited': RunStatus.SUCCESS,
            'dead': RunStatus.FAILED,
        }
        if status in status_map:
            return status_map[status]

        return RunStatus.UNKNOWN


class DockerSchedule(BackendSchedule):

    _run = None

    @property
    def status(self):
        if not self._run:
            return RunStatus.UNSTARTED
        else:
            return self._run.status

    @staticmethod
    def _remap_files(subject):
        mapping = {}
        subject = copy.deepcopy(subject)

        if isinstance(subject, str):
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
                subject[key], submapping = DockerSchedule._remap_files(val)
                mapping.update(submapping)
            return subject, mapping

        elif isinstance(subject, list):
            for key, val in enumerate(subject):
                subject[key], submapping = DockerSchedule._remap_files(val)
                mapping.update(submapping)
            return subject, mapping


class DockerDataSettingsSchedule(DockerSchedule, DataSettingsSchedule):

    def run(self):
        output_folder = tempfile.mkdtemp()

        volumes = {
            output_folder: {'bind': '/output_folder', 'mode': 'rw'},
            '/tmp': {'bind': '/scratch', 'mode': 'rw'},
        }

        data_settings = self.data_settings
        shutil.copy(data_settings, os.path.join(output_folder, 'data_settings.yml'))

        container_args = [
            '/',
            '/output_folder',
            'cli',
            '--',
            'utils',
            'data_config',
            'build',
            '/output_folder/data_settings.yml',
        ]

        self._run = DockerRun(self.backend.client.containers.run(
            'fcpindi/c-pac:' + self.backend.tag,
            command=container_args,
            detach=True,
            working_dir='/output_folder',
            volumes=volumes
        ))

        self._run.container.wait()
        
        try:
            files = glob.glob(os.path.join(output_folder, 'cpac_data_config_*.yml'))
            if files:
                with open(files[0]) as f:
                    self._results['data_config'] = yaml.safe_load(f)
        finally:
            shutil.rmtree(output_folder)


class DockerDataConfigSchedule(DataConfigSchedule, DockerSchedule):

    def run(self):
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
                    self._results['data_config'] = yaml.safe_load(f)
        finally:
            shutil.rmtree(self._output_folder)


class DockerParticipantPipelineSchedule(ParticipantPipelineSchedule, DockerSchedule):

    def run(self):
        config_folder = tempfile.mkdtemp()
        output_folder = tempfile.mkdtemp()

        if self.pipeline is not None:
            new_pipeline = os.path.join(config_folder, 'pipeline.yml')
            shutil.copy(self.pipeline, new_pipeline)

        volumes = {
            '/tmp': {'bind': '/scratch', 'mode': 'rw'},
            config_folder: {'bind': '/config', 'mode':'ro'},
            output_folder: {'bind': '/output', 'mode':'rw'},
        }

        subject = 'data:text/plain;base64,' + \
            b64encode(yaml.dump([self.subject], default_flow_style=False).encode("utf-8")).decode("utf-8")

        # TODO handle local databases, transverse subject dict to get folder mappings
        command = [
            '/', '/output', 'participant',
            '--monitoring',
            '--skip_bids_validator',
            '--save_working_dir',
            '--data_config_file',
            subject
        ]

        if self.pipeline:
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

        try:
            http_client = httpclient.HTTPClient()
            response = json.loads(http_client.fetch("http://localhost:%d/" % port).body.decode('utf-8'))
            return response
        except Exception as e:
            print(e)  # TODO handle reading error
        finally:
            http_client.close()

        return []


class DockerBackend(Backend):

    tag = 'nightly'

    base_schedule_class = DockerSchedule

    schedule_mapping = {
        Schedule: DockerSchedule,
        DataSettingsSchedule: DockerDataSettingsSchedule,
        DataConfigSchedule: DockerDataConfigSchedule,
        ParticipantPipelineSchedule: DockerParticipantPipelineSchedule,
    }

    def __init__(self, scheduler=None, tag=None):
        self.client = docker.from_env()
        try:
            self.client.ping()
        except docker.errors.APIError:
            raise "Could not connect to Docker"

        self.scheduler = scheduler
        self.tag = tag or DockerBackend.tag
