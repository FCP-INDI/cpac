import asyncio
import copy
import glob
import hashlib
import json
import logging
import os
import pkgutil
import shutil
import tempfile
import time
import uuid
from functools import reduce
from subprocess import PIPE, STDOUT, Popen

import yaml
from tornado.websocket import websocket_connect

from cpac.api.client import Client

from ...utils import yaml_parse
from ..schedules import (DataConfigSchedule, DataSettingsSchedule,
                         ParticipantPipelineSchedule, Schedule)
from .base import Backend, BackendSchedule, RunStatus
from .utils import find_free_port, merge_async_iters

logger = logging.getLogger(__name__)

class SLURMSchedule(BackendSchedule):

    _status = None
    _prefix = 'cpacpy-slurm_'

    @property
    async def status(self):
        if not self._status:
            return RunStatus.UNSTARTED
        return self._status

    async def pre(self):
        pass

    async def post(self):
        pass

    async def run(self):
        self._job_id = self.backend.start_job(f'cpacpy_{repr(self)}', '')
        logger.info(f'[{self}] Job ID {self._job_id}')

        while self._status is not RunStatus.RUNNING:
            await asyncio.sleep(1)
            status = self.backend.queue_info(self._job_id)

            self._status = status[self._job_id]['STATE']
            logger.info(f'[{self}] Job status {self._status}')

        self._proxy_addr = self.backend.proxy(self._job_id)
        logger.info(f'[{self}] Job proxy {self._proxy_addr[0]}:{self._proxy_addr[1]}')

        status = None
        try:
            async with Client(self._proxy_addr) as client:
                logger.info(f'[{self}] Scheduling {self}')
                schedule = await client.schedule(self)
                logger.info(f'[{self}] Job scheduled {schedule}')
                async for message in client.listen(self):
                    logger.info(f'[{self}] Job message {message}')
                    yield message
                    if isinstance(message, Schedule.End):
                        status = message.status
                self._results = await client.result(self)
        finally:
            self.backend.unproxy(self._job_id)
            self.backend.cancel_job(self._job_id)
            self._status = status if status else RunStatus.FAILURE


class SLURMDataSettingsSchedule(SLURMSchedule, DataSettingsSchedule):
    pass

class SLURMDataConfigSchedule(SLURMSchedule, DataConfigSchedule):
    pass

class SLURMParticipantPipelineSchedule(SLURMSchedule, ParticipantPipelineSchedule):
    pass

class SLURMBackend(Backend):

    base_schedule_class = SLURMSchedule

    schedule_mapping = {
        Schedule: SLURMSchedule,
        DataSettingsSchedule: SLURMDataSettingsSchedule,
        DataConfigSchedule: SLURMDataConfigSchedule,
        ParticipantPipelineSchedule: SLURMParticipantPipelineSchedule,
    }

    def __init__(self, id, host, username, key, control, node_backend=None, pip_install=None, scheduler=None):
        super().__init__(id=id, scheduler=scheduler)

        self.host = host.split(':')
        self.username = username
        self.key = key
        self.node_backend = node_backend
        self.pip_install = pip_install

        self._forwards = {}

        self.control = control

        try:
            os.remove(self.control)
        except: #TODO treat specific exception
            pass
        
        self._control_args = [
            '-o', f'ControlPath={self.control}',
            '-o', 'ControlMaster=auto',
            '-o', 'ControlPersist=15m',
        ]

        logger.info(f'[{self}] Control {self.control} {self._control_args}')

        self.connect()

    def connect(self):
        if os.path.exists(self.control):
            return

        cmd = [
            'ssh',
            '-T',
            '-p', self.host[1],
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null', # TODO enable host key check
        ]

        if self.key:
            cmd += [
                '-i', self.key,
            ] 
            
        cmd += self._control_args + [
            f'{self.username}@{self.host[0]}'
        ]

        stdout, stderr = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate(b"\n")
        # TODO handle exit code
        # print("Connect")
        # print(stdout)
        # print(stderr)

    def copy(self, src, dst):
        cmd = [
            'scp',
            '-BCr'
        ] + self._control_args + [
            src,
            f'dummy:{dst}'
        ]
        stdout, stderr = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate(b"\n")
        # TODO handle exit code
        # print("Copy")
        # print(stdout)
        # print(stderr)


    def exec(self, command):
        cmd = [
            'ssh',
            '-T',
            '-p', self.host[1],
        ] + self._control_args + [
            'dummy',
        ] + command
        proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate(b"\n")
        returncode = proc.returncode
        return returncode, stdout, stderr

    def queue_info(self, jobs=None):
        query = []
        if jobs:
            jobs = [jobs] if type(jobs) is not list else jobs
            jobs = [int(j) for j in jobs]
            query = ['--jobs', ','.join(str(j) for j in jobs)]

        _, queue, _ = self.exec(
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

    def cancel_all(self):
        status = self.queue_info()
        ret, out, err = self.exec(['scancel'] + [str(j) for j in status.keys()])

    def start_job(self, job_name, time):
        slurm_template = pkgutil.get_data(__package__, 'data/slurm.sh').decode()
        slurm_script = slurm_template \
            .replace('$JOB_NAME', job_name) \
            .replace('$PIP_INSTALL', self.pip_install) \
            .replace('$TIME', '0-05:00:00')

        _, slurm_script_name = tempfile.mkstemp(prefix='cpacpy-slurm_', suffix='.sh')
        with open(slurm_script_name, 'w') as f:
            f.write(slurm_script)

        self.copy(slurm_script_name, '/tmp/cpacpy-slurm.sh')
        ret, job, error = self.exec(['sbatch', '--parsable', '/tmp/cpacpy-slurm.sh'])
        
        try:
            os.remove(slurm_script_name)
        except:
            pass

        try:
            return int(job)
        except ValueError:
            raise Exception(error.decode())

    def cancel_job(self, job):
        logger.info(f'[SLURMBackend] Cancelling job {job}')
        ret, stdout, stderr = self.exec(['scancel', str(job)])

    def proxy(self, job_id):
        status = self.queue_info(job_id)[job_id]
        if status['STATE'] is not RunStatus.RUNNING:
            return

        port = find_free_port()
        forward = f'0.0.0.0:{port}:{status["NODELIST"]}:3333'
        self._forwards[job_id] = forward

        cmd = [
            'ssh',
            '-T',
            '-L', forward
            ] + self._control_args + [
            'dummy',
        ]
        Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate(b"\n")
        return ('localhost', port)

    def unproxy(self, job_id):
        cmd = [
            'ssh',
            '-T',
            '-O', 'cancel',
            '-L', self._forwards[job_id]
            ] + self._control_args + [
            'dummy',
        ]
        Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate(b"\n")
