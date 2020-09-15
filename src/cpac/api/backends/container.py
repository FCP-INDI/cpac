import asyncio
import copy
import glob
import hashlib
import json
import logging
import os
import shutil
import tempfile
import time
import uuid

import yaml
from tornado.websocket import websocket_connect

from ...utils import yaml_parse
from ..schedules import (DataConfigSchedule, DataSettingsSchedule,
                         ParticipantPipelineSchedule, Schedule)
from .base import (Backend, BackendSchedule, RunStatus,
                   FileResult, LogFileResult, CrashFileResult)
from .utils import find_free_port, merge_async_iters, struuid

logger = logging.getLogger(__name__)

class ContainerSchedule(BackendSchedule):

    _status = None
    _prefix = 'cpacpy-container_'

    @property
    async def status(self):
        if not self._status:
            return RunStatus.UNSTARTED
        return self._status

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
                subject[key], submapping = ContainerSchedule._remap_files(val)
                mapping.update(submapping)
            return subject, mapping

        elif isinstance(subject, list):
            for key, val in enumerate(subject):
                subject[key], submapping = ContainerSchedule._remap_files(val)
                mapping.update(submapping)
            return subject, mapping


class ContainerDataSettingsSchedule(ContainerSchedule, DataSettingsSchedule):

    async def run(self):
        output_folder = tempfile.mkdtemp(prefix=self._prefix)

        volumes = {
            output_folder: {'bind': '/output_folder', 'mode': 'rw'},
            '/tmp': {'bind': '/scratch', 'mode': 'rw'},
        }

        data_settings_file = os.path.join(output_folder, 'data_settings.yml')

        if isinstance(self.data_settings, str):
            if '\n' in self.data_settings:
                self.data_settings = yaml.safe_load(self.data_settings)
            else:
                self.data_settings = yaml_parse(self.data_settings)

        with open(data_settings_file, 'w') as f:
            yaml.dump(self.data_settings, f)

        command = [
            '/',
            '/output_folder',
            'cli',
            '--',
            'utils',
            'data_config',
            'build',
            '/output_folder/data_settings.yml',
        ]

        async for item in self._runner(command, volumes):
            yield BackendSchedule.Status(
                schedule=self,
                timestamp=item["time"],
                status=item["status"],
            )

        try:
            files = glob.glob(os.path.join(output_folder, 'cpac_data_config_*.yml'))
            if files:
                with open(files[0]) as f:
                    self._results['data_config'] = yaml.safe_load(f)
 
                yield BackendSchedule.Result(
                    schedule=self,
                    result=self._results['data_config'],
                    timestamp=time.time(),
                    key='data_config',
                )
        finally:
            shutil.rmtree(output_folder)


class ContainerDataConfigSchedule(ContainerSchedule, DataConfigSchedule):

    async def run(self):
        run_folder = tempfile.mkdtemp(prefix=self._prefix)
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

        command = [data_folder or '/dev/null', '/output', 'test_config']
        if data_config:
            command += ['--data_config_file', '/config/data_config.yml']

        async for item in self._runner(command, volumes):
            yield BackendSchedule.Status(
                schedule=self,
                timestamp=item["time"],
                status=item["status"],
            )

        try:
            files = glob.glob(os.path.join(output_folder, 'cpac_data_config_*.yml'))
            if files:
                with open(files[0]) as f:
                    self._results['data_config'] = yaml.safe_load(f)

                yield BackendSchedule.Result(
                    schedule=self,
                    result=self._results['data_config'],
                    timestamp=time.time(),
                    key='data_config',
                )
        finally:
            shutil.rmtree(output_folder)


class ContainerParticipantPipelineSchedule(ContainerSchedule,
                                        ParticipantPipelineSchedule):

    async def run(self):
        run_folder = tempfile.mkdtemp(prefix='cpacpy-docker_')
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

        self._run_logs_port = find_free_port()

        command = [
            '/', '/output', 'participant',
            '--monitoring', str(self._run_logs_port),
            '--skip_bids_validator',
            '--save_working_dir',
            '--data_config_file',
            mapped_data_config
        ]

        if pipeline:
            command += ['--pipeline_file', pipeline]

        self._status = None
        self._run_logs_last = None
        self._run_logs_messages = asyncio.Queue()

        self._logs_messages = []

        started_at = time.time()

        merged, _, cancel_tasks = merge_async_iters(
            self._logger_listener(),
            self._file_listener(output_folder),
            self._runner(command, volumes, port=self._run_logs_port)
        )

        async for item in merged:
            if item["type"] == "log":
                if item["content"]["type"] == "node":
                    self._logs_messages.append(item["content"])
                    yield BackendSchedule.Log(
                        schedule=self,
                        timestamp=item["time"],
                        content=item["content"],
                    )
                elif item["content"]["type"] == "file":
                    content = item["content"]

                    result_type = {
                        "log": LogFileResult,
                        "crash": CrashFileResult,
                    }[content["filetype"]]

                    key_type = { "log": "logs", "crash": "crashes" }[content['filetype']]
                    key = struuid(content["path"], namespace=self.uid)

                    if key_type not in self._results:
                        self._results[key_type] = {}
                    self._results[key_type][key] = result_type(content["path"])

                    yield BackendSchedule.Result(
                        schedule=self,
                        result=self._results[key_type][key],
                        timestamp=item["time"],
                        key=f"{key_type}/{key}",
                    )

            elif item["type"] == "status":
                yield BackendSchedule.Status(
                    schedule=self,
                    timestamp=item["time"],
                    status=item["status"],
                )

        await cancel_tasks()

        self._results["time"] = time.time() - started_at

    @property
    async def logs(self):
        if self._status == RunStatus.RUNNING:
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

    async def _file_listener(self, output_folder):
        sent_files = set([])
        while True:
            logs = set(glob.glob(os.path.join(output_folder, 'log', 'pipeline_*', '*', 'pypeline.log'))) - sent_files
            crashes = set(glob.glob(os.path.join(output_folder, 'crash', 'crash-*.pklz'))) - sent_files
            for f in logs:
                yield {
                    "type": "log",
                    "time": time.time(),
                    "content": {
                        "type": "file",
                        "filetype": "log",
                        "path": f,
                    }
                }
                sent_files |= set([f])

            for f in crashes:
                yield {
                    "type": "log",
                    "time": time.time(),
                    "content": {
                        "type": "file",
                        "filetype": "crash",
                        "path": f,
                    }
                }
                sent_files |= set([f])

            await asyncio.sleep(0.5)
            yield

    async def _logger_listener(self):

        while self._status is None:
            await asyncio.sleep(0.1)

        while self._status != RunStatus.RUNNING:
            await asyncio.sleep(0.1)

        port = self._run_logs_port
        uri = f"ws://localhost:{port}/log"

        while True:
            ws = None
            try:
                ws = await websocket_connect(uri)
                await ws.write_message(json.dumps({
                    "time": time.time(),
                    "message": {
                        "last_log": self._run_logs_last,
                    }
                }))
                while True:
                    try:
                        msg = await asyncio.wait_for(ws.read_message(), timeout=1)
                        if msg is None:
                            break
                        msg = json.loads(msg)
                        self._run_logs_last = msg["time"]
                        yield {
                            "type": "log",
                            "time": msg["time"],
                            "content": { "type": "node", **msg["message"] },
                        }
                    except asyncio.TimeoutError:
                        await asyncio.sleep(0.1)
            except:
                await asyncio.sleep(0.1)
                yield
            finally:
                if ws:
                    ws.close()


class ContainerBackend(Backend):

    base_schedule_class = ContainerSchedule

    schedule_mapping = {
        Schedule: ContainerSchedule,
        DataSettingsSchedule: ContainerDataSettingsSchedule,
        DataConfigSchedule: ContainerDataConfigSchedule,
        ParticipantPipelineSchedule: ContainerParticipantPipelineSchedule,
    }
