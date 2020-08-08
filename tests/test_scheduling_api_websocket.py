import asyncio
import datetime
import json
import logging
import os
from itertools import groupby

import numpy as np
import pytest
import tornado
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


    with open(os.path.join(Constants.TESTS_DATA_PATH, 'data_config_template.yml'), 'r') as f:
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
            messages += [message]

            if message['type'] != 'watch':
                continue

            data = message['data']

            schedule_id, message_type, message = data['id'], data['type'], data['message']
            if message_type == 'Start':
                schedules_alive |= set([schedule_id])
            if message_type == 'Spawn':
                schedules_alive |= set([message['schedule']])
            if message_type == 'End':
                schedules_alive ^= set([schedule_id])

    except Exception as e:
        import traceback
        traceback.print_exc()

    await scheduler

    boundaries = sorted(
        [
            {
                'schedule': m['data']['id'],
                **m['data']['message']
            }
            for m in messages
            if m['data']['type'] in ('Start', 'End')
        ],
        key=lambda l: l['schedule']
    )

    logs = sorted(
        [
            {
                'schedule': m['data']['id'],
                **m['data']['message']['content']
            }
            for m in messages
            if m['data']['type'] == 'Log'
        ],
        key=lambda l: l['schedule']
    )

    first_logs = {
        sid: min(slogs, key=lambda l: l['start'])['start']
        for sid, slogs in groupby(logs, lambda l: l['schedule'])
    }
    latest_first_log = max(first_logs.values())

    last_logs = { 
        sid: max(slogs, key=lambda l: l['end'])['end']
        for sid, slogs in groupby(logs, lambda l: l['schedule'])
    }
    earliest_last_log = min(last_logs.values())

    # Test if they are run in parallel
    # The lastest node-start report must come before the earliest node-end report

    #                 ↓ earliest end
    # 1  ######  ######
    # 2    ######  ######
    # 3   ######  ######
    # 4      ######  ######
    #        ↑ latest start

    #                 ↓ earliest end
    # 1  ######  ######
    # 2                 ######  ######
    # 3                                ######  ######
    # 4                                               ######  ######
    #                                                 ↑ latest start

    assert latest_first_log < earliest_last_log
    
    assert np.std([last_logs[sid] - start for sid, start in first_logs.items()]) < 0.05
    
    ws_client.close()
