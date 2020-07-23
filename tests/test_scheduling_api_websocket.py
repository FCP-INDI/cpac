import asyncio
import json
import logging
import os

import pytest
import tornado
import datetime
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
async def test_data_config_logs(app, http_client, base_url, scheduler):

    ws_base_url = base_url.replace('http', 'ws')
    ws_url = f'{ws_base_url}/schedule/connect'
    ws_client = await tornado.websocket.websocket_connect(ws_url)

    welcome = json.loads(await ws_client.read_message())
    assert welcome['connected']


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

    await ws_client.write_message(json.dumps({
        "type": "watch",
        "schedule": schedule,
        "children": True,
    }))

    schedules_alive = set([schedule])
    messages = []
    try:
        while len(schedules_alive):
            message = json.loads(await ws_client.read_message())
            if message['type'] != 'watch':
                continue

            data = message['data']
            messages += [data]

            message_type, message = data['type'], data['message']
            if message_type in ('Start', 'Spawn'):
                schedules_alive |= set([message['schedule']])
            if message_type == 'End':
                schedules_alive ^= set([message['schedule']])

            print("schedules_alive", schedules_alive)

    except Exception as e:
        import traceback
        traceback.print_exc()

    await scheduler

    # TODO test messages
    for m in messages:
        print(m)

    ws_client.close()