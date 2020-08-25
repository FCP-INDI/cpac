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
from functools import reduce
from subprocess import PIPE, STDOUT, Popen

import yaml
from tornado.websocket import websocket_connect

from ...utils import yaml_parse
from ..schedules import (DataConfigSchedule, DataSettingsSchedule,
                         ParticipantPipelineSchedule, Schedule)
from .base import Backend, BackendSchedule, RunStatus
from .utils import merge_async_iters, find_free_port

logger = logging.getLogger(__name__)

class SLURMSchedule(BackendSchedule):

    _run_status = None
    _prefix = 'cpacpy-slurm_'

    @property
    async def status(self):
        if not self._run_status:
            return RunStatus.UNSTARTED
        return self._run_status


class SLURMDataSettingsSchedule(SLURMSchedule, DataSettingsSchedule):

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
                timestamp=item["time"],
                status=item["status"],
            )

        try:
            files = glob.glob(os.path.join(output_folder, 'cpac_data_config_*.yml'))
            if files:
                with open(files[0]) as f:
                    self._results['data_config'] = yaml.safe_load(f)
        finally:
            shutil.rmtree(output_folder)


class SLURMDataConfigSchedule(SLURMSchedule, DataConfigSchedule):

    async def run(self):
        run_folder = tempfile.mkdtemp(prefix='cpacpy-docker_')
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
                timestamp=item["time"],
                status=item["status"],
            )

        try:
            files = glob.glob(os.path.join(output_folder, 'cpac_data_config_*.yml'))
            if files:
                with open(files[0]) as f:
                    self._results['data_config'] = yaml.safe_load(f)
        finally:
            shutil.rmtree(output_folder)


class SLURMParticipantPipelineSchedule(SLURMSchedule,
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
        if self._run_status == RunStatus.RUNNING:
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

    async def _logger_listener(self):

        while self._run_status is None:
            await asyncio.sleep(0.1)

        while self._run_status != RunStatus.RUNNING:
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
                await asyncio.sleep(0.1)
                yield
            finally:
                if ws:
                    ws.close()


class SLURMBackend(Backend):

    base_schedule_class = SLURMSchedule

    schedule_mapping = {
        Schedule: SLURMSchedule,
        DataSettingsSchedule: SLURMDataSettingsSchedule,
        DataConfigSchedule: SLURMDataConfigSchedule,
        ParticipantPipelineSchedule: SLURMParticipantPipelineSchedule,
    }

    def __init__(self, host, username, password, node_backend=None, scheduler=None):
        self.scheduler = scheduler
        self.host = host.split(':')
        self.username = username
        self.password = password
        self.node_backend = node_backend

        # TODO parametrize
        self._controlsock = '/tmp/controlpath.sock'
        self._forwards = {}

        try:
            os.remove(self._controlsock)
        except:
            pass

        self._control_args = [
            '-o', f'ControlPath={self._controlsock}',
            '-o', 'ControlMaster=auto',
            '-o', 'ControlPersist=15m',
        ]

        self.connect()


    def connect(self):
        cmd = [
            'ssh',
            '-T',
            '-p', self.host[1],
            '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null', # TODO enable host key check
            '-i', '/home/anibalsolon/Documents/cpac-python-package/tests/test_data/slurm/compose-cluster/id_rsa',
            ] + self._control_args + [
            f'{self.username}@{self.host[0]}'
        ]
        conn = Popen(cmd, stdin=PIPE)
        conn.communicate(b"\n")

    def copy(self, src, dst):
        cmd = [
            'scp',
            '-BCr'
            ] + self._control_args + [
            src,
            f'dummy:{dst}'
        ]
        conn = Popen(cmd, stdin=PIPE)
        conn.communicate(b"\n")

    def exec(self, command):
        cmd = [
            'ssh',
            '-T',
            '-p', self.host[1],
            # '-i', '/home/anibalsolon/Documents/cpac-python-package/tests/test_data/slurm/compose-cluster/id_rsa',
            ] + self._control_args + [
            'dummy',
        ] + command
        conn = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = conn.communicate(b"\n")
        return stdout, stderr

    async def queue_info(self, jobs=None):
        query = []
        if jobs:
            jobs = [jobs] if type(jobs) is not list else jobs
            jobs = [int(j) for j in jobs]
            query = ['--jobs', ','.join(str(j) for j in jobs)]

        queue, _ = self.exec(
            ['squeue'] + query +
            ['--Format=JobId,Name,Account,BatchHost,Partition,Priority,StartTime,State,TimeUsed,WorkDir,NodeList']
        )
        queue = queue.decode()
        queue = queue.split('\n')
        header, *data = queue
        data = list(filter(None, data))
        header_values = list(filter(None, header.split(' ')))
        header_pos = reduce(lambda acc, h: acc + [header.index(h, acc[-1])], header_values, [None])[1:]
        header_range = list(zip(header_pos, header_pos[1:] + [None]))

        data_pieces = [dict(zip(header_values, [d[f:t].strip() for (f, t) in header_range])) for d in data]
        for pieces in data_pieces:
            # days-hours:minutes:seconds
            days, time = f'0-{pieces["TIME"]}'.split('-')[-2:]
            hours, minutes, seconds = f'0:0:{time}'.split(':')[-3:]
            pieces['TIME'] = int(seconds) + (int(minutes) * 60) + (int(hours) * 60 * 60) + (int(days) * 24 * 60 * 60)

            pieces['STATE'] = {
                'PENDING': RunStatus.UNSTARTED,
                'RESIZING': RunStatus.UNSTARTED,
                'CONFIGURING': RunStatus.UNSTARTED,
                'RUNNING': RunStatus.RUNNING,
                'COMPLETING': RunStatus.RUNNING,
                'COMPLETED': RunStatus.SUCCESS,
            }.get(pieces['STATE'], RunStatus.FAILURE)

        data_pieces = { int(d['JOBID']): d for d in data_pieces }

        if jobs:
            data_pieces = {
                j: data_pieces.get(j, {
                    'JOBID': j,
                    'STATE': RunStatus.UNKNOWN,
                })
                for j in jobs
            }
        return data_pieces

    async def cancel_all(self):
        status = await self.queue_info()
        out, err = self.exec(['scancel'] + [str(j) for j in status.keys()])

    async def run_on_node(self, job_name, time):

        with open('/home/anibalsolon/Documents/cpac-python-package/src/cpac/api/data/slurm.sh') as f:
            slurm_template = f.read()

        slurm_script = slurm_template.format(
            job_name=job_name,
            time='0-05:00:00'
        )

        with open('/tmp/cpacpy-slurm.sh', 'w') as f:
            f.write(slurm_script)

        self.copy('/tmp/cpacpy-slurm.sh', '/tmp/cpacpy-slurm.sh')
        job, _ = self.exec(['sbatch', '--parsable', '/tmp/cpacpy-slurm.sh'])

        return int(job)

    async def proxy(self, job_id):
        status = (await self.queue_info(job_id))[job_id]
        if status['STATE'] is not RunStatus.RUNNING:
            return

        port = find_free_port()

        # ssh -O cancel -S/tmp/controlpath.sock -L 22442:c2:3333 dummy

        forward = f'0.0.0.0:{port}:{status["NODELIST"]}:3333'
        self._forwards[job_id] = forward

        cmd = [
            'ssh',
            '-T',
            '-L', forward
            ] + self._control_args + [
            'dummy',
        ]
        conn = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = conn.communicate(b"\n")
        return ('localhost', port)