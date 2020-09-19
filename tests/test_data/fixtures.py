import os
import re
import time
import yaml
import tempfile
import pytest
import asyncio
import subprocess
import logging
from datetime import timedelta
from cpac.api.backends.docker import DockerBackend
from cpac.api.backends.singularity import SingularityBackend
from cpac.api.backends.slurm import SLURMBackend
from cpac.api.scheduling import Scheduler
from cpac.api.server import app as app_obj
from cpac.api.backends.utils import wait_for_port, process

from test_data.docker import build_image as docker_build_image
from test_data.singularity import build_image as singularity_build_image


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
    return SingularityBackend(id="singularitu", image=image)

def slurm_config():
    return {
        'host': 'localhost:22222',
        'username': 'root',
        'key': os.path.join(this_dir, 'slurm/id_rsa'),
        'control': tempfile.mkstemp(prefix='cpacpy-slurm_', suffix='.sock')[1],
        'pip_install': '-e /code',
    }

def slurm_backend():
    slurm_dir = os.path.join(this_dir, 'slurm')
    logger.info(f'[Fixtures] Starting SLURM cluster')

    start_at = time.time()
    process(['docker-compose', 'down', '-v'], cwd=slurm_dir)
    process(['docker-compose', 'up', '-d'], cwd=slurm_dir)

    logger.info(f'[Fixtures] Building Singularity image')
    image = singularity_build_image(type='simg')
    config = slurm_config()
    wait_for_port(config['host'])

    with open(os.path.join(slurm_dir, 'docker-compose.yml'), 'r') as f:
        compose = yaml.safe_load(f)
    services = compose['services'].keys()

    logger.info(f'[Fixtures] Copying Singularity image to cluster nodes')
    for node in [n for n in services if re.match(r'c[0-9]+', n)]:
        container_id, _ = process(['docker-compose', 'ps', '-q', node], cwd=slurm_dir)
        container_id = container_id.decode().strip()
        process(['docker', 'cp', image, f'{container_id}:/opt/cpacpy-singularity_test.simg'])

    time_diff = int(time.time() - start_at)
    logger.info(f'[Fixtures] SLURM cluster up ({timedelta(seconds=time_diff)})')
    return SLURMBackend(id="slurm", **slurm_config())

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
