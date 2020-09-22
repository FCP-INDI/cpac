import os
import pytest
import asyncio
import subprocess
import logging
from cpac.api.backends.docker import DockerBackend
from cpac.api.backends.singularity import SingularityBackend
from cpac.api.backends.slurm import SLURMBackend
from cpac.api.scheduling import Scheduler
from cpac.api.server import app as app_obj
from cpac.api.backends.utils import wait_for_port, process

from test_data.docker import build_image as docker_build_image
from test_data.singularity import build_image as singularity_build_image
from test_data.slurm import start_cluster as singularity_start_cluster

this_dir = os.path.dirname(__file__)
logger = logging.getLogger(__name__)

@pytest.fixture(scope='function')
def event_loop(io_loop):
    loop = io_loop.current().asyncio_loop
    yield loop
    loop.stop()

def docker_backend():
    image = docker_build_image()
    return DockerBackend(id="docker", image=image)

def singularity_backend():
    image = singularity_build_image()
    return SingularityBackend(id="singularity", image=image)

def slurm_backend():
    config = singularity_start_cluster()
    backend = SLURMBackend(id="slurm", **config)
    backend.connect()
    backend.cancel_all()
    return SLURMBackend(id="slurm", **config)

backend_params = [singularity_backend, docker_backend, slurm_backend]

@pytest.fixture(params=backend_params)
async def backend(request):
    backend = request.param()
    return backend

@pytest.fixture(params=backend_params)
async def scheduler(request):
    backend = request.param()
    async with Scheduler(backend) as scheduler:
        yield scheduler
        await scheduler

@pytest.fixture
def app(scheduler):
    app_obj.settings['scheduler'] = scheduler
    return app_obj
