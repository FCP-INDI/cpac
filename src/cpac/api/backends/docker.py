import copy
import glob
import hashlib
import json
import os
import sys
import shutil
import tempfile
import time
import zlib
import asyncio
import logging
import websockets
import datetime
from base64 import b64decode, b64encode

from tornado.websocket import websocket_connect

from .utils import merge_async_iters
from ...utils import yaml_parse

import yaml
import docker

from ..schedules import (DataConfigSchedule, DataSettingsSchedule,
                         ParticipantPipelineSchedule, Schedule)
from .base import Backend, BackendSchedule, RunStatus


logger = logging.getLogger('cpac.api.backends.docker')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

docker_statuses = {
    'created': RunStatus.STARTING,
    'restarting': RunStatus.RUNNING,
    'running': RunStatus.RUNNING,
    'removing': RunStatus.RUNNING,
    'paused': RunStatus.RUNNING,
    'exited': RunStatus.SUCCESS,
    'dead': RunStatus.FAILED,
}

class DockerSchedule(BackendSchedule):

    _run = None

    @property
    async def status(self):
        if not self._run:
            return RunStatus.UNSTARTED

        try:
            self._run.reload()
        except Exception:
            return RunStatus.UNKNOWN

        status = self._run.status
        if status in docker_statuses:
            return docker_statuses[status]

        return RunStatus.UNKNOWN

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

    async def run(self):
        output_folder = tempfile.mkdtemp()

        volumes = {
            output_folder: {'bind': '/output_folder', 'mode': 'rw'},
            '/tmp': {'bind': '/scratch', 'mode': 'rw'},
        }

        data_settings = yaml_parse(self.data_settings)
        with open(os.path.join(output_folder, 'data_settings.yml'), 'w') as f:
            yaml.dump(data_settings, f)

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

        self._run = self.backend.client.containers.run(
            'fcpindi/c-pac:' + self.backend.tag,
            command=container_args,
            detach=True,
            working_dir='/output_folder',
            volumes=volumes
        )

        self._run.wait()

        try:
            files = glob.glob(os.path.join(output_folder, 'cpac_data_config_*.yml'))
            if files:
                with open(files[0]) as f:
                    self._results['data_config'] = yaml.safe_load(f)
        finally:
            shutil.rmtree(output_folder)


class DockerDataConfigSchedule(DockerSchedule, DataConfigSchedule):

    async def run(self):
        run_folder = tempfile.mkdtemp()
        config_folder = os.path.join(run_folder, 'config')
        output_folder = os.path.join(run_folder, 'output')

        os.makedirs(config_folder)
        os.makedirs(output_folder)

        volumes = {
            '/tmp': {'bind': '/scratch', 'mode': 'rw'},
            config_folder: {'bind': '/config', 'mode': 'ro'},
            output_folder: {'bind': '/output', 'mode': 'rw'},
        }

        data_folder = None
        data_config = None
        try:
            data_config_data = self.data_config
            if isinstance(data_config_data, str):
                data_config_data = yaml_parse(data_config_data)

            data_config = os.path.join(config_folder, 'data_config.yml')
            with open(data_config, 'w') as f:
                yaml.dump(data_config_data, f)

        except ValueError:
            data_folder = self.data_config

        if data_folder and not data_folder.startswith('s3://'):
            volumes[data_folder] = {'bind': '/data_folder', 'mode': 'ro'}
            data_folder = '/data_folder'

        container_args = [data_folder, '/output', 'test_config']

        if data_config:
            container_args += ['--data_config_file', '/config/data_config.yml']

        self._run = self.backend.client.containers.run(
            'fcpindi/c-pac:' + self.backend.tag,
            command=container_args,
            detach=True,
            volumes=volumes
        )

        self._run.wait()

        try:
            files = glob.glob(os.path.join(output_folder, 'cpac_data_config_*.yml'))
            if files:
                with open(files[0]) as f:
                    self._results['data_config'] = yaml.safe_load(f)
        finally:
            shutil.rmtree(output_folder)


class DockerParticipantPipelineSchedule(DockerSchedule, ParticipantPipelineSchedule):

    async def run(self):
        run_folder = tempfile.mkdtemp()
        config_folder = os.path.join(run_folder, 'config')
        output_folder = os.path.join(run_folder, 'output')

        os.makedirs(config_folder)
        os.makedirs(output_folder)

        pipeline = None
        if self.pipeline is not None:
            pipeline = os.path.join(config_folder, 'pipeline.yml')
            shutil.copy(self.pipeline, pipeline)

        volumes = {
            '/tmp': {'bind': '/scratch', 'mode': 'rw'},
            config_folder: {'bind': '/config', 'mode':'ro'},
            output_folder: {'bind': '/output', 'mode':'rw'},
        }

        data_config = os.path.join(config_folder, 'data_config.yml')
        mapped_data_config = '/config/data_config.yml'
        if isinstance(self.subject, str):
            shutil.copy(self.subject, data_config)
        else:
            with open(data_config, 'w') as f:
                yaml.dump([self.subject], f)

        command = [
            '/', '/output', 'participant',
            '--monitoring',
            '--skip_bids_validator',
            '--save_working_dir',
            '--data_config_file',
            mapped_data_config
        ]

        if pipeline:
            command += ['--pipeline_file', pipeline]

        self._run_status = None
        self._run_logs_port = 8008
        self._run_logs_last = None
        self._run_logs_messages = asyncio.Queue()

        self._logs_messages = []

        async for item in merge_async_iters(
            self._logger_listener(),
            self._runner(command, volumes)
        ):
            if item["type"] == "log":
                self._logs_messages.append(item["content"])
                yield BackendSchedule.Log(
                    timestamp=item["time"],
                    content=item["content"],
                )
            elif item["type"] == "status":
                yield BackendSchedule.Status(
                    timestamp=item["time"],
                    status=item["status"],
                )

        self._run_status = None

    @property
    async def logs(self):
        if self._run_status in ['running', 'created']:
            for log in self._logs_messages:
                yield log
            while True:
                log = await self._run_logs_messages.get()
                self._logs_messages += [log]
                yield log
                self._run_logs_messages.task_done()
        else:
            for log in self._logs_messages:
                yield log

    async def _runner(self, command, volumes):
        container = self.backend.client.containers.run(
            'fcpindi/c-pac:' + self.backend.tag,
            command=command,
            detach=True,
            stdin_open=False,
            ports={'8008/tcp': None},
            volumes=volumes,
        )

        await asyncio.sleep(3)
        container.reload()

        self._run_logs_port = int(container.attrs['NetworkSettings']['Ports']['8008/tcp'][0]['HostPort'])

        while True:
            try:
                await asyncio.sleep(0.5)

                container.reload()
                status = container.status
                if self._run_status == status:
                    continue

                self._run_status = status
                logger.info(f"Got status {status}")

                yield {
                    "type": "status",
                    "time": time.time(),
                    "status": container.status,
                }

                if status not in ['running', 'created']:
                    break
            except docker.errors.NotFound:
                break

        try:
            container.remove(v=True, force=True)
        except:
            pass


    async def _logger_listener(self):

        while self._run_status is None:
            await asyncio.sleep(0.1)

        while self._run_status not in ['running']:
            logger.info("Waiting container to start")
            await asyncio.sleep(0.5)

        port = int(self._run_logs_port)
        uri = f"ws://localhost:{port}/log"

        while True:
            try:
                ws = await websocket_connect(uri)
                await ws.write_message(json.dumps({
                    "time": time.time(),
                    "message": {
                        "last_log": self._run_logs_last,
                    }
                }))
                while True:
                    msg = await ws.read_message()
                    if msg is None:
                        break
                    msg = json.loads(msg)
                    self._run_logs_last = msg["time"]
                    yield {
                        "type": "log",
                        "time": msg["time"],
                        "content": msg["message"],
                    }
            except:
                logger.info("Waiting monitoring to start")
                await asyncio.sleep(1)
                yield
            finally:
                ws.close()


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
