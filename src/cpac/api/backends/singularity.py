import asyncio
import logging
import subprocess
import time

from ..schedules import (DataConfigSchedule, DataSettingsSchedule,
                         ParticipantPipelineSchedule, Schedule)
from .base import RunStatus
from .container import (ContainerBackend, ContainerDataConfigSchedule,
                        ContainerDataSettingsSchedule,
                        ContainerParticipantPipelineSchedule,
                        ContainerSchedule)

from .utils import find_free_port

logger = logging.getLogger(__name__)


class SingularitySchedule(ContainerSchedule):

    _prefix = 'cpacpy-singularity_'

    async def _runner(self, command, volumes, port=None):

        proc_command = [
            'singularity',
            'run',
            '--fakeroot',
        ]

        if port:
            proc_command += [
                '--network', 'bridge',
                '--network-args',
                f'portmap={port}:{port}/tcp',
            ]
            self._run_logs_port = int(port)

        for host_dir, container_dir in volumes.items():
            proc_command += [
                '-B', f'{host_dir}:{container_dir["bind"]}' # {":" + container_dir["mode"] if container_dir.get("mode") else ""}'
            ]

        proc_command += [self.backend.image]
        proc_command += command

        self._run_process = subprocess.Popen(proc_command)

        status_code = self._run_process.poll()
        while status_code is None:
            await asyncio.sleep(1)
            try:
                self._run_process.wait(timeout=0.1)
            except subprocess.TimeoutExpired:
                pass
                
            self._status = RunStatus.RUNNING
            status_code = self._run_process.poll()

        self._status = RunStatus.SUCCESS if status_code == 0 else RunStatus.FAILURE

        yield {
            "type": "status",
            "time": time.time(),
            "status": self._status
        }


class SingularityDataSettingsSchedule(SingularitySchedule,
                                      ContainerDataSettingsSchedule,
                                      DataSettingsSchedule):
    pass


class SingularityDataConfigSchedule(SingularitySchedule,
                                    ContainerDataConfigSchedule,
                                    DataConfigSchedule):
    pass


class SingularityParticipantPipelineSchedule(SingularitySchedule,
                                             ContainerParticipantPipelineSchedule,
                                             ParticipantPipelineSchedule):
    pass


class SingularityBackend(ContainerBackend):

    image = 'shub://FCP-INDI/C-PAC:latest'

    base_schedule_class = SingularitySchedule

    schedule_mapping = {
        Schedule: SingularitySchedule,
        DataSettingsSchedule: SingularityDataSettingsSchedule,
        DataConfigSchedule: SingularityDataConfigSchedule,
        ParticipantPipelineSchedule: SingularityParticipantPipelineSchedule,
    }

    def __init__(self, scheduler=None, image=None):
        # TODO test singularity is installed
        self.scheduler = scheduler
        self.image = image or SingularityBackend.image
