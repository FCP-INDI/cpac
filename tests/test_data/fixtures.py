import pytest
import asyncio
from cpac.api.backends.docker import DockerBackend
from cpac.api.backends.singularity import SingularityBackend
from cpac.api.scheduling import Scheduler
from cpac.api.server import app as app_obj

from test_data.docker import build_image as docker_build_image
from test_data.singularity import build_image as singularity_build_image


@pytest.fixture(scope='function')
def event_loop(io_loop):
    loop = io_loop.current().asyncio_loop
    yield loop
    loop.stop()


def docker_backend():
    image = docker_build_image()
    return DockerBackend(image=image)


def singularity_backend():
    image = singularity_build_image()
    return SingularityBackend(image=image)


@pytest.fixture(params=[singularity_backend, docker_backend])
async def backend(request):
    backend = request.param()
    return backend


@pytest.fixture(params=[singularity_backend, docker_backend])
async def scheduler(request):
    backend = request.param()
    async with Scheduler(backend) as scheduler:
        yield scheduler
        await scheduler


@pytest.fixture
def app(scheduler):
    app_obj.settings['scheduler'] = scheduler
    return app_obj