import asyncio
import json
import logging
import os

import pytest
from tornado.escape import json_decode

from conftest import Constants
from cpac import __version__
from cpac.api.backends.docker import DockerBackend
from cpac.api.scheduling import Scheduler
from cpac.api.server import app as app_obj
from cpac.utils import generate_data_url

try:
    from test_data.docker import build_image
except:
    pytest.skip("Skipping docker tests", allow_module_level=True)


@pytest.fixture(scope='function')
def event_loop(io_loop):
    loop = io_loop.current().asyncio_loop
    yield loop
    loop.stop()

@pytest.fixture
def docker_tag():
    build_image(tag='docker-test')
    return 'docker-test'

@pytest.fixture
def backend(docker_tag):
    return DockerBackend(tag=docker_tag)

@pytest.fixture
async def scheduler(backend):
    async with Scheduler(backend) as scheduler:
        yield scheduler
        await scheduler

@pytest.fixture
def app(scheduler):
    app_obj.settings['scheduler'] = scheduler
    return app_obj


@pytest.mark.asyncio
@pytest.mark.gen_test(timeout=2)
async def test_version(http_client, base_url):
    response = await http_client.fetch(base_url, raise_error=False)
    assert response.code == 200
    assert json_decode(response.body) == {'api': 'cpacpy', 'version': __version__}


@pytest.mark.asyncio
@pytest.mark.gen_test(timeout=2)
async def test_data_settings(http_client, base_url, scheduler):

    with open(os.path.join(Constants.TESTS_DATA_PATH, 'data_settings_template.yml'), 'r') as f:
        data_settings = f.read()

    # Schedule a data_settings => data_config conversion
    body = json.dumps({
        'type': 'data_settings', 
        'data_settings': generate_data_url(data_settings, 'text/yaml'),
    })
    response = await http_client.fetch(f'{base_url}/schedule', method='POST', headers=None, body=body, raise_error=False)
    assert response.code == 200

    body = json_decode(response.body)
    assert 'schedule' in body
    schedule = body['schedule']

    # Check before there are results
    response = await http_client.fetch(f'{base_url}/schedule/{schedule}/result', raise_error=False)
    assert response.code == 425

    await scheduler

    # Check when it get results
    response = await http_client.fetch(f'{base_url}/schedule/{schedule}/result', raise_error=False)
    body = json_decode(response.body)

    assert 'result' in body
    result = body['result']

    assert 'data_config' in result
    data_config = result['data_config']

    assert len(data_config) == 4


@pytest.mark.asyncio
@pytest.mark.gen_test(timeout=2)
async def test_data_settings(http_client, base_url, scheduler):

    with open(os.path.join(Constants.TESTS_DATA_PATH, 'data_settings_template.yml'), 'r') as f:
        data_settings = f.read()

    # Schedule a data_settings => data_config conversion
    body = json.dumps({
        'type': 'data_settings', 
        'data_settings': generate_data_url(data_settings, 'text/yaml'),
    })
    response = await http_client.fetch(f'{base_url}/schedule', method='POST', headers=None, body=body, raise_error=False)
    assert response.code == 200

    body = json_decode(response.body)
    assert 'schedule' in body
    schedule = body['schedule']

    # Check before there are results
    response = await http_client.fetch(f'{base_url}/schedule/{schedule}/result', raise_error=False)
    assert response.code == 425

    await scheduler

    # Check when it get results
    response = await http_client.fetch(f'{base_url}/schedule/{schedule}/result', raise_error=False)
    body = json_decode(response.body)

    assert 'result' in body
    result = body['result']

    assert 'data_config' in result
    data_config = result['data_config']

    assert len(data_config) == 4


@pytest.mark.asyncio
@pytest.mark.gen_test(timeout=2)
async def test_data_config(http_client, base_url, scheduler):

    with open(os.path.join(Constants.TESTS_DATA_PATH, 'data_config_template_single.yml'), 'r') as f:
        data_config = f.read()

    body = json.dumps({
        'type': 'pipeline', 
        'data_config': generate_data_url(data_config, 'text/yaml'),
    })
    response = await http_client.fetch(
        f'{base_url}/schedule',
        method='POST',
        headers=None,
        body=body,
        raise_error=False
    )
    assert response.code == 200

    body = json_decode(response.body)
    assert 'schedule' in body
    schedule = body['schedule']

    # Check before there are results
    response = await http_client.fetch(f'{base_url}/schedule/{schedule}/result', raise_error=False)
    assert response.code == 425

    await asyncio.sleep(1)

    response = await http_client.fetch(f'{base_url}/schedule/{schedule}/status', raise_error=False)
    body = json_decode(response.body)
    assert body['status'] == 'RUNNING'

    await scheduler

    # Check when it get results
    response = await http_client.fetch(f'{base_url}/schedule/{schedule}/result', raise_error=False)
    body = json_decode(response.body)

    assert 'result' in body
    result = body['result']

    assert 'data_config' in result
    data_config = result['data_config']

    assert len(data_config) == 1

    # Look for the spawned child
    assert 'children' in body
    children = body['children']

    assert len(children) == 1

    child = children[0]
    response = await http_client.fetch(f'{base_url}/schedule/{child}/result', raise_error=False)

    # TODO add a result for participant run
    # body = json_decode(response.body)
    # print(body)